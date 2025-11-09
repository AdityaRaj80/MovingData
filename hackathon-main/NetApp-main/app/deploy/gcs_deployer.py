"""Utility to package the application source and upload it to Google Cloud Storage.

This module provides a small CLI that tars and compresses the repository and then
uploads the artifact to the configured GCS bucket. The helper respects the
``GOOGLE_APPLICATION_CREDENTIALS`` and ``GCP_PROJECT_ID`` environment variables
so that the deployment can run inside CI/CD or local terminals without
additional setup beyond a service-account key file.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import io
import os
import pathlib
import sys
import tarfile
from typing import Optional

from google.auth.exceptions import DefaultCredentialsError
from google.cloud import storage


def _resolve_root(path: Optional[str]) -> pathlib.Path:
    """Resolve the directory that should be bundled for deployment."""
    if path is None:
        return pathlib.Path(__file__).resolve().parents[1]
    resolved = pathlib.Path(path).expanduser().resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"Source path '{resolved}' does not exist")
    if not resolved.is_dir():
        raise NotADirectoryError(f"Source path '{resolved}' is not a directory")
    return resolved


def _create_archive(source: pathlib.Path) -> io.BytesIO:
    """Create an in-memory tar.gz archive of the source directory."""
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
        archive.add(str(source), arcname=source.name)
    buffer.seek(0)
    return buffer


def _build_object_name(prefix: Optional[str], source: pathlib.Path) -> str:
    timestamp = _dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    base_name = f"{source.name}-{timestamp}.tar.gz"
    if prefix:
        prefix = prefix.strip("/")
        return f"{prefix}/{base_name}" if prefix else base_name
    return base_name


def _get_storage_client(credentials_path: Optional[str], project_id: Optional[str]) -> storage.Client:
    try:
        if credentials_path:
            return storage.Client.from_service_account_json(credentials_path, project=project_id)
        return storage.Client(project=project_id)
    except DefaultCredentialsError as exc:
        raise RuntimeError(
            "No Google Cloud credentials found. Provide GOOGLE_APPLICATION_CREDENTIALS "
            "or configure application-default credentials."
        ) from exc


def upload_to_gcs(
    bucket_name: str,
    *,
    source_dir: Optional[str] = None,
    object_prefix: Optional[str] = None,
    credentials_path: Optional[str] = None,
    project_id: Optional[str] = None,
) -> str:
    """Package the application source and upload it to the configured bucket.

    Returns the gs:// URI of the uploaded artifact.
    """
    if not bucket_name:
        raise ValueError("A target GCS bucket must be provided")

    source_path = _resolve_root(source_dir)
    archive_buffer = _create_archive(source_path)
    object_name = _build_object_name(object_prefix, source_path)

    env_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    env_project = os.getenv("GCP_PROJECT_ID")
    client = _get_storage_client(credentials_path or env_credentials, project_id or env_project)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(object_name)
    blob.upload_from_file(archive_buffer, rewind=True, content_type="application/gzip")

    return f"gs://{bucket_name}/{object_name}"


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Upload the application source as a GCS deployment artifact.")
    parser.add_argument("bucket", help="Name of the destination GCS bucket")
    parser.add_argument(
        "--source",
        dest="source",
        help="Path to the directory that should be archived. Defaults to the application root.",
    )
    parser.add_argument(
        "--prefix",
        dest="prefix",
        help="Optional folder prefix to apply to the uploaded object.",
    )
    parser.add_argument(
        "--project",
        dest="project",
        help="Override the GCP project ID if it differs from the environment variable.",
    )
    parser.add_argument(
        "--credentials",
        dest="credentials",
        help="Path to a service account JSON file. Defaults to GOOGLE_APPLICATION_CREDENTIALS.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    try:
        target_uri = upload_to_gcs(
            args.bucket,
            source_dir=args.source,
            object_prefix=args.prefix,
            credentials_path=args.credentials,
            project_id=args.project,
        )
    except (RuntimeError, OSError, ValueError) as exc:
        print(f"Deployment failed: {exc}", file=sys.stderr)
        return 1

    print(f"Uploaded deployment package to {target_uri}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
