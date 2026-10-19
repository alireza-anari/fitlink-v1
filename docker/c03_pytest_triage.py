"""Opt-in metadata-only pytest evidence; never record locals or payload text."""

import ast
import json
import os
import re
import sys
import threading
import time
from pathlib import Path

import pytest

# Finite public Chromium error names; no arbitrary exception token is emitted.
# Source: https://github.com/chromium/chromium/blob/405665065117459f6a72161b865c8244742b21c7/net/base/net_error_list.h
NET_ERROR_CODES = frozenset(
    """
ERR_IO_PENDING
ERR_FAILED
ERR_ABORTED
ERR_INVALID_ARGUMENT
ERR_INVALID_HANDLE
ERR_FILE_NOT_FOUND
ERR_TIMED_OUT
ERR_FILE_TOO_BIG
ERR_UNEXPECTED
ERR_ACCESS_DENIED
ERR_NOT_IMPLEMENTED
ERR_INSUFFICIENT_RESOURCES
ERR_OUT_OF_MEMORY
ERR_UPLOAD_FILE_CHANGED
ERR_SOCKET_NOT_CONNECTED
ERR_FILE_EXISTS
ERR_FILE_PATH_TOO_LONG
ERR_FILE_NO_SPACE
ERR_FILE_VIRUS_INFECTED
ERR_BLOCKED_BY_CLIENT
ERR_NETWORK_CHANGED
ERR_BLOCKED_BY_ADMINISTRATOR
ERR_SOCKET_IS_CONNECTED
ERR_UPLOAD_STREAM_REWIND_NOT_SUPPORTED
ERR_CONTEXT_SHUT_DOWN
ERR_BLOCKED_BY_RESPONSE
ERR_CLEARTEXT_NOT_PERMITTED
ERR_BLOCKED_BY_CSP
ERR_H2_OR_QUIC_REQUIRED
ERR_BLOCKED_BY_ORB
ERR_NETWORK_ACCESS_REVOKED
ERR_BLOCKED_BY_FINGERPRINTING_PROTECTION
ERR_BLOCKED_IN_INCOGNITO_BY_ADMINISTRATOR
ERR_LOCAL_NETWORK_PERMISSION_MISSING
ERR_STRICT_ECH_REQUIRED
ERR_CONNECTION_CLOSED
ERR_CONNECTION_RESET
ERR_CONNECTION_REFUSED
ERR_CONNECTION_ABORTED
ERR_CONNECTION_FAILED
ERR_NAME_NOT_RESOLVED
ERR_INTERNET_DISCONNECTED
ERR_SSL_PROTOCOL_ERROR
ERR_ADDRESS_INVALID
ERR_ADDRESS_UNREACHABLE
ERR_SSL_CLIENT_AUTH_CERT_NEEDED
ERR_TUNNEL_CONNECTION_FAILED
ERR_NO_SSL_VERSIONS_ENABLED
ERR_SSL_VERSION_OR_CIPHER_MISMATCH
ERR_SSL_RENEGOTIATION_REQUESTED
ERR_PROXY_AUTH_UNSUPPORTED
ERR_BAD_SSL_CLIENT_AUTH_CERT
ERR_CONNECTION_TIMED_OUT
ERR_HOST_RESOLVER_QUEUE_TOO_LARGE
ERR_SOCKS_CONNECTION_FAILED
ERR_SOCKS_CONNECTION_HOST_UNREACHABLE
ERR_ALPN_NEGOTIATION_FAILED
ERR_SSL_NO_RENEGOTIATION
ERR_WINSOCK_UNEXPECTED_WRITTEN_BYTES
ERR_SSL_DECOMPRESSION_FAILURE_ALERT
ERR_SSL_BAD_RECORD_MAC_ALERT
ERR_PROXY_AUTH_REQUESTED
ERR_PROXY_CONNECTION_FAILED
ERR_MANDATORY_PROXY_CONFIGURATION_FAILED
ERR_PRECONNECT_MAX_SOCKET_LIMIT
ERR_SSL_CLIENT_AUTH_PRIVATE_KEY_ACCESS_DENIED
ERR_SSL_CLIENT_AUTH_CERT_NO_PRIVATE_KEY
ERR_PROXY_CERTIFICATE_INVALID
ERR_NAME_RESOLUTION_FAILED
ERR_NETWORK_ACCESS_DENIED
ERR_TEMPORARILY_THROTTLED
ERR_HTTPS_PROXY_TUNNEL_RESPONSE_REDIRECT
ERR_SSL_CLIENT_AUTH_SIGNATURE_FAILED
ERR_MSG_TOO_BIG
ERR_WS_PROTOCOL_ERROR
ERR_ADDRESS_IN_USE
ERR_SSL_HANDSHAKE_NOT_COMPLETED
ERR_SSL_BAD_PEER_PUBLIC_KEY
ERR_SSL_PINNED_KEY_NOT_IN_CERT_CHAIN
ERR_CLIENT_AUTH_CERT_TYPE_UNSUPPORTED
ERR_SSL_DECRYPT_ERROR_ALERT
ERR_WS_THROTTLE_QUEUE_TOO_LARGE
ERR_SSL_SERVER_CERT_CHANGED
ERR_SSL_UNRECOGNIZED_NAME_ALERT
ERR_SOCKET_SET_RECEIVE_BUFFER_SIZE_ERROR
ERR_SOCKET_SET_SEND_BUFFER_SIZE_ERROR
ERR_SOCKET_RECEIVE_BUFFER_SIZE_UNCHANGEABLE
ERR_SOCKET_SEND_BUFFER_SIZE_UNCHANGEABLE
ERR_SSL_CLIENT_AUTH_CERT_BAD_FORMAT
ERR_ICANN_NAME_COLLISION
ERR_SSL_SERVER_CERT_BAD_FORMAT
ERR_CT_STH_PARSING_FAILED
ERR_CT_STH_INCOMPLETE
ERR_UNABLE_TO_REUSE_CONNECTION_FOR_PROXY_AUTH
ERR_CT_CONSISTENCY_PROOF_PARSING_FAILED
ERR_SSL_OBSOLETE_CIPHER
ERR_WS_UPGRADE
ERR_READ_IF_READY_NOT_IMPLEMENTED
ERR_NO_BUFFER_SPACE
ERR_SSL_CLIENT_AUTH_NO_COMMON_ALGORITHMS
ERR_EARLY_DATA_REJECTED
ERR_WRONG_VERSION_ON_EARLY_DATA
ERR_TLS13_DOWNGRADE_DETECTED
ERR_SSL_KEY_USAGE_INCOMPATIBLE
ERR_INVALID_ECH_CONFIG_LIST
ERR_ECH_NOT_NEGOTIATED
ERR_ECH_FALLBACK_CERTIFICATE_INVALID
ERR_PROXY_UNABLE_TO_CONNECT_TO_DESTINATION
ERR_PROXY_DELEGATE_CANCELED_CONNECT_REQUEST
ERR_PROXY_DELEGATE_CANCELED_CONNECT_RESPONSE
ERR_CONTROL_MSG_TOO_BIG
ERR_MULTICAST_NOT_ALLOWED
ERR_CERT_COMMON_NAME_INVALID
ERR_CERT_DATE_INVALID
ERR_CERT_AUTHORITY_INVALID
ERR_CERT_CONTAINS_ERRORS
ERR_CERT_NO_REVOCATION_MECHANISM
ERR_CERT_UNABLE_TO_CHECK_REVOCATION
ERR_CERT_REVOKED
ERR_CERT_INVALID
ERR_CERT_WEAK_SIGNATURE_ALGORITHM
ERR_CERT_NON_UNIQUE_NAME
ERR_CERT_WEAK_KEY
ERR_CERT_NAME_CONSTRAINT_VIOLATION
ERR_CERT_VALIDITY_TOO_LONG
ERR_CERTIFICATE_TRANSPARENCY_REQUIRED
ERR_CERT_KNOWN_INTERCEPTION_BLOCKED
ERR_CERT_SELF_SIGNED_LOCAL_NETWORK
ERR_CERT_END
ERR_INVALID_URL
ERR_DISALLOWED_URL_SCHEME
ERR_UNKNOWN_URL_SCHEME
ERR_INVALID_REDIRECT
ERR_TOO_MANY_REDIRECTS
ERR_UNSAFE_REDIRECT
ERR_UNSAFE_PORT
ERR_INVALID_RESPONSE
ERR_INVALID_CHUNKED_ENCODING
ERR_METHOD_NOT_SUPPORTED
ERR_UNEXPECTED_PROXY_AUTH
ERR_EMPTY_RESPONSE
ERR_RESPONSE_HEADERS_TOO_BIG
ERR_PAC_SCRIPT_FAILED
ERR_REQUEST_RANGE_NOT_SATISFIABLE
ERR_MALFORMED_IDENTITY
ERR_CONTENT_DECODING_FAILED
ERR_NETWORK_IO_SUSPENDED
ERR_SYN_REPLY_NOT_RECEIVED
ERR_ENCODING_CONVERSION_FAILED
ERR_UNRECOGNIZED_FTP_DIRECTORY_LISTING_FORMAT
ERR_INVALID_SPDY_STREAM
ERR_NO_SUPPORTED_PROXIES
ERR_HTTP2_PROTOCOL_ERROR
ERR_INVALID_AUTH_CREDENTIALS
ERR_UNSUPPORTED_AUTH_SCHEME
ERR_ENCODING_DETECTION_FAILED
ERR_MISSING_AUTH_CREDENTIALS
ERR_UNEXPECTED_SECURITY_LIBRARY_STATUS
ERR_MISCONFIGURED_AUTH_ENVIRONMENT
ERR_UNDOCUMENTED_SECURITY_LIBRARY_STATUS
ERR_RESPONSE_BODY_TOO_BIG_TO_DRAIN
ERR_RESPONSE_HEADERS_MULTIPLE_CONTENT_LENGTH
ERR_INCOMPLETE_HTTP2_HEADERS
ERR_PAC_NOT_IN_DHCP
ERR_RESPONSE_HEADERS_MULTIPLE_CONTENT_DISPOSITION
ERR_RESPONSE_HEADERS_MULTIPLE_LOCATION
ERR_HTTP2_SERVER_REFUSED_STREAM
ERR_HTTP2_PING_FAILED
ERR_PIPELINE_EVICTION
ERR_CONTENT_LENGTH_MISMATCH
ERR_INCOMPLETE_CHUNKED_ENCODING
ERR_QUIC_PROTOCOL_ERROR
ERR_RESPONSE_HEADERS_TRUNCATED
ERR_QUIC_HANDSHAKE_FAILED
ERR_REQUEST_FOR_SECURE_RESOURCE_OVER_INSECURE_QUIC
ERR_HTTP2_INADEQUATE_TRANSPORT_SECURITY
ERR_HTTP2_FLOW_CONTROL_ERROR
ERR_HTTP2_FRAME_SIZE_ERROR
ERR_HTTP2_COMPRESSION_ERROR
ERR_PROXY_AUTH_REQUESTED_WITH_NO_CONNECTION
ERR_HTTP_1_1_REQUIRED
ERR_PROXY_HTTP_1_1_REQUIRED
ERR_PAC_SCRIPT_TERMINATED
ERR_PROXY_REQUIRED
ERR_TEMPORARY_BACKOFF
ERR_INVALID_HTTP_RESPONSE
ERR_CONTENT_DECODING_INIT_FAILED
ERR_HTTP2_RST_STREAM_NO_ERROR_RECEIVED
ERR_HTTP2_PUSHED_STREAM_NOT_AVAILABLE
ERR_HTTP2_CLAIMED_PUSHED_STREAM_RESET_BY_SERVER
ERR_TOO_MANY_RETRIES
ERR_HTTP2_STREAM_CLOSED
ERR_HTTP2_CLIENT_REFUSED_STREAM
ERR_HTTP2_PUSHED_RESPONSE_DOES_NOT_MATCH
ERR_HTTP_RESPONSE_CODE_FAILURE
ERR_QUIC_CERT_ROOT_NOT_KNOWN
ERR_QUIC_GOAWAY_REQUEST_CAN_BE_RETRIED
ERR_TOO_MANY_ACCEPT_CH_RESTARTS
ERR_INCONSISTENT_IP_ADDRESS_SPACE
ERR_CACHED_IP_ADDRESS_SPACE_BLOCKED_BY_LOCAL_NETWORK_ACCESS_POLICY
ERR_BLOCKED_BY_LOCAL_NETWORK_ACCESS_CHECKS
ERR_ZSTD_WINDOW_SIZE_TOO_BIG
ERR_DICTIONARY_LOAD_FAILED
ERR_UNEXPECTED_CONTENT_DICTIONARY_HEADER
ERR_CACHE_MISS
ERR_CACHE_READ_FAILURE
ERR_CACHE_WRITE_FAILURE
ERR_CACHE_OPERATION_NOT_SUPPORTED
ERR_CACHE_OPEN_FAILURE
ERR_CACHE_CREATE_FAILURE
ERR_CACHE_RACE
ERR_CACHE_CHECKSUM_READ_FAILURE
ERR_CACHE_CHECKSUM_MISMATCH
ERR_CACHE_LOCK_TIMEOUT
ERR_CACHE_AUTH_FAILURE_AFTER_READ
ERR_CACHE_ENTRY_NOT_SUITABLE
ERR_CACHE_DOOM_FAILURE
ERR_CACHE_OPEN_OR_CREATE_FAILURE
ERR_CACHE_COMPRESSION_FAILURE
ERR_INSECURE_RESPONSE
ERR_NO_PRIVATE_KEY_FOR_CERT
ERR_ADD_USER_CERT_FAILED
ERR_INVALID_SIGNED_EXCHANGE
ERR_INVALID_WEB_BUNDLE
ERR_TRUST_TOKEN_OPERATION_FAILED
ERR_TRUST_TOKEN_OPERATION_SUCCESS_WITHOUT_SENDING_REQUEST
ERR_HTTPENGINE_PROVIDER_IN_USE
ERR_PKCS12_IMPORT_BAD_PASSWORD
ERR_PKCS12_IMPORT_FAILED
ERR_IMPORT_CA_CERT_NOT_CA
ERR_IMPORT_CERT_ALREADY_EXISTS
ERR_IMPORT_CA_CERT_FAILED
ERR_IMPORT_SERVER_CERT_FAILED
ERR_PKCS12_IMPORT_INVALID_MAC
ERR_PKCS12_IMPORT_INVALID_FILE
ERR_PKCS12_IMPORT_UNSUPPORTED
ERR_KEY_GENERATION_FAILED
ERR_PRIVATE_KEY_EXPORT_FAILED
ERR_SELF_SIGNED_CERT_GENERATION_FAILED
ERR_CERT_DATABASE_CHANGED
ERR_CERT_VERIFIER_CHANGED
ERR_DNS_MALFORMED_RESPONSE
ERR_DNS_SERVER_REQUIRES_TCP
ERR_DNS_TIMED_OUT
ERR_DNS_CACHE_MISS
ERR_DNS_SEARCH_EMPTY
ERR_DNS_SORT_ERROR
ERR_DNS_SECURE_RESOLVER_HOSTNAME_RESOLUTION_FAILED
ERR_DNS_NAME_HTTPS_ONLY
ERR_DNS_REQUEST_CANCELLED
ERR_DNS_NO_MATCHING_SUPPORTED_ALPN
ERR_DNS_SECURE_PROBE_RECORD_INVALID
ERR_DNS_CACHE_INVALIDATION_IN_PROGRESS
ERR_DNS_FORMAT_ERROR
ERR_DNS_SERVER_FAILURE
ERR_DNS_NOT_IMPLEMENTED
ERR_DNS_REFUSED
ERR_DNS_OTHER_FAILURE
ERR_DNS_DIRECT_ONLY
ERR_BLOB_INVALID_CONSTRUCTION_ARGUMENTS
ERR_BLOB_OUT_OF_MEMORY
ERR_BLOB_FILE_WRITE_FAILED
ERR_BLOB_SOURCE_DIED_IN_TRANSIT
ERR_BLOB_DEREFERENCED_WHILE_BUILDING
ERR_BLOB_REFERENCED_BLOB_BROKEN
ERR_BLOB_REFERENCED_FILE_UNAVAILABLE
""".split()
)

ROOT = Path(__file__).resolve().parents[1]
TESTS = {}
for path in (ROOT / "tests").rglob("test_*.py"):
    TESTS[path.relative_to(ROOT).as_posix()] = {
        n.name
        for n in ast.walk(ast.parse(path.read_text()))
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def safe_node(node):
    node = node.split("[", 1)[0]
    parts = node.split("::")
    if len(parts) >= 2 and parts[-1] in TESTS.get(parts[0], set()):
        return node
    return "<redacted>"


def location(filename, function, line):
    try:
        path = Path(filename).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        path = "<external>"
        # Pytest's rewritten cache can retain the host compile-time filename
        # when mounted into a container. Normalize only known static test code.
        for known_file, functions in TESTS.items():
            if filename.endswith("/" + known_file) and function in functions:
                path = known_file
                break
        for package in ("_pytest", "pluggy", "django", "psycopg", "rest_framework"):
            if path == "<external>" and f"/{package}/" in filename:
                path = package + "/" + filename.split(f"/{package}/", 1)[1]
                break
        if Path(filename).name in {
            "subprocess.py",
            "threading.py",
            "selectors.py",
            "socket.py",
        }:
            path = Path(filename).name
    return {
        "file": path,
        "function": function if re.fullmatch(r"[\w<>.]+", function) else "<redacted>",
        "line": line,
    }


def stacks():
    result = []
    for identifier, frame in list(sys._current_frames().items())[:16]:
        rows = []
        while frame and len(rows) < 80:
            rows.append(
                location(frame.f_code.co_filename, frame.f_code.co_name, frame.f_lineno)
            )
            frame = frame.f_back
        result.append({"thread": identifier, "frames": rows})
    return result


class Journal:
    def __init__(self, path, cutoff=0.25, session_cutoff=120, terminate=False):
        self.output = Path(path).open("x")
        self.started = time.monotonic()
        self.case_started = None
        self.node = None
        self.last_node = None
        self.phase = "collection"
        self.cutoff = cutoff
        self.session_cutoff = session_cutoff
        self.terminate = terminate
        self.recorded = False
        self.session_recorded = False
        self.lock = threading.Lock()
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self.observe, daemon=True)
        self.thread.start()

    def emit(self, event, **values):
        with self.lock:
            self.output.write(
                json.dumps(
                    {
                        "event": event,
                        "elapsed_seconds": round(time.monotonic() - self.started, 3),
                        **values,
                    },
                    sort_keys=True,
                )
                + "\n"
            )
            self.output.flush()

    def begin(self, node):
        self.node = safe_node(node)
        self.last_node = self.node
        self.case_started = time.monotonic()
        self.recorded = False
        self.phase = "setup"
        self.emit("test_start", node=self.node)

    def snapshot(self, event):
        from docker.c03_gate_diagnostics import process_rows

        self.emit(
            event,
            active_node=self.node,
            phase=self.phase,
            case_seconds=round(time.monotonic() - self.case_started, 3)
            if self.case_started
            else None,
            stacks=stacks(),
            owned_processes=process_rows(b"C03_TRIAGE_OWNER=", owner_pid=os.getpid()),
        )

    def observe(self):
        while not self.stop.wait(0.02):
            if (
                self.case_started
                and not self.recorded
                and time.monotonic() - self.case_started >= self.cutoff
            ):
                self.recorded = True
                self.snapshot("case_cutoff")
            if (
                not self.session_recorded
                and time.monotonic() - self.started >= self.session_cutoff
            ):
                self.session_recorded = True
                self.snapshot(
                    "diagnostic_cutoff" if self.terminate else "session_snapshot"
                )
                if self.terminate:
                    os._exit(124)

    def finish(self):
        self.stop.set()
        self.thread.join(timeout=1)
        self.emit("observer_finished")
        self.output.close()


JOURNAL = None


def pytest_configure(config):
    global JOURNAL
    path = os.environ.get("C03_TRIAGE_EVIDENCE_FILE")
    if path:
        foundation = os.environ.get("C03_FOUNDATION_TRIAGE") == "1"
        JOURNAL = Journal(
            path,
            cutoff=30 if foundation else 0.05,
            session_cutoff=120,
            terminate=not foundation,
        )


@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_runtest_protocol(item, nextitem):
    if JOURNAL:
        JOURNAL.begin(item.nodeid)
    try:
        return (yield)
    finally:
        if JOURNAL:
            JOURNAL.emit(
                "test_end",
                node=JOURNAL.node,
                case_seconds=round(time.monotonic() - JOURNAL.case_started, 3),
            )
            JOURNAL.node = None
            JOURNAL.case_started = None


def pytest_runtest_setup(item):
    if JOURNAL:
        JOURNAL.phase = "setup"


def pytest_runtest_call(item):
    if JOURNAL:
        JOURNAL.phase = "call"


def pytest_runtest_teardown(item, nextitem):
    if JOURNAL:
        JOURNAL.phase = "teardown"


def failure_data(info):
    data = {"exception": info.type.__name__}
    # Only finite labels leave the process: browser messages may contain private
    # URLs, submitted values or tokens. Never emit the message or call log.
    if info.type.__module__.startswith("playwright."):
        message = str(info.value)
        folded = message.casefold()
        data["browser_failure_flags"] = [
            label
            for marker, label in (
                ("protocol", "protocol"),
                ("navigat", "navigation"),
                ("frame", "frame"),
                ("detach", "detached"),
                ("closed", "closed"),
                ("crash", "crashed"),
                ("interrupt", "interrupted"),
                ("cancel", "cancelled"),
                ("download", "download"),
                ("dialog", "dialog"),
                ("net::", "network"),
                ("connect", "connection"),
                ("history", "history"),
                ("context", "context"),
                ("document", "document"),
                ("resource", "resource"),
                ("not attached", "not_attached"),
            )
            if marker in folded
        ]
        code = re.search(r"\bnet::(ERR_[A-Z0-9_]{1,80})\b", message)
        if code and code[1] in NET_ERROR_CODES:
            data["browser_net_error"] = code[1]
        data["browser_failure_category"] = next(
            (
                label
                for marker, label in (
                    ("interrupted by another navigation", "navigation_interrupted"),
                    ("ERR_CONNECTION_REFUSED", "connection_refused"),
                    ("ERR_ABORTED", "request_aborted"),
                    ("ERR_HTTP_RESPONSE_CODE_FAILURE", "http_response_failure"),
                    ("ERR_EMPTY_RESPONSE", "empty_response"),
                    ("ERR_CACHE_MISS", "cache_miss"),
                    ("ERR_FAILED", "network_failed"),
                    ("ERR_NETWORK_CHANGED", "network_changed"),
                    ("ERR_TIMED_OUT", "network_timeout"),
                    ("ERR_CONNECTION_RESET", "connection_reset"),
                    ("ERR_CONNECTION_CLOSED", "connection_closed"),
                    ("Frame was detached", "frame_detached"),
                    ("Page crashed", "page_crashed"),
                    ("has been closed", "target_closed"),
                    ("Timeout", "timeout"),
                )
                if marker in message
            ),
            "other",
        )
        if data["browser_failure_category"] == "other":
            if "browser_net_error" in data:
                data["browser_failure_category"] = "network_error"
            elif "protocol" in data["browser_failure_flags"]:
                data["browser_failure_category"] = "protocol_error"
    data["traceback"] = [
        location(str(e.path), e.frame.code.name, e.lineno + 1) for e in info.traceback
    ]
    for entry in info.traceback:
        response = entry.frame.f_locals.get("response")
        if response is not None and type(getattr(response, "status_code", None)) is int:
            data["actual_http_status"] = response.status_code
            try:
                source = str(entry.statement)
            except (AssertionError, IndexError, OSError):
                # Optional source text can disappear or never exist for a frame.
                # Retain the original exception/status without replacing its verdict.
                source = ""
                known_file = location(
                    str(entry.path), entry.frame.code.name, entry.lineno
                )["file"]
                if known_file in TESTS:
                    try:
                        source = (
                            (ROOT / known_file).read_text().splitlines()[entry.lineno]
                        )
                    except (OSError, IndexError):
                        pass
            expected = re.search(r"assert response.status_code == ([0-9]{3})", source)
            if expected:
                data["expected_http_status"] = int(expected[1])
                data["assertion"] = "assert response.status_code == " + expected[1]
    return data


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item, call):
    report = yield
    if JOURNAL:
        data = {
            "node": safe_node(item.nodeid),
            "phase": report.when,
            "outcome": report.outcome,
            "seconds": round(report.duration, 3),
        }
        if call.excinfo:
            data.update(failure_data(call.excinfo))
        JOURNAL.emit("test_report", **data)
    return report


def pytest_sessionfinish(session, exitstatus):
    if JOURNAL:
        JOURNAL.emit("pytest_exit", exitstatus=int(exitstatus))
        JOURNAL.finish()


def pytest_internalerror(excrepr, excinfo):
    if JOURNAL:
        # Never read exception text, frame locals or longrepr for a framework error.
        from docker.c03_storage_errors import error_category

        JOURNAL.emit(
            "pytest_internalerror",
            active_node=JOURNAL.node or JOURNAL.last_node,
            exception=error_category(excinfo.value),
            traceback=[
                location(str(e.path), e.frame.code.name, e.lineno + 1)
                for e in excinfo.traceback
            ],
        )
