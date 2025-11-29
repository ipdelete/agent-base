"""Aegis gRPC protocol buffer definitions."""

from agent.proto.aegis_pb2 import (
    ExecuteRequest,
    ExecutionChunk,
    ExecutionError,
    ExecutionResponse,
    HealthRequest,
    HealthResponse,
)
from agent.proto.aegis_pb2_grpc import AegisControllerStub

__all__ = [
    "ExecuteRequest",
    "ExecutionChunk",
    "ExecutionError",
    "ExecutionResponse",
    "HealthRequest",
    "HealthResponse",
    "AegisControllerStub",
]
