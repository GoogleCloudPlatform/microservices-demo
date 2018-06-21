#!/bin/bash -e

# protos are loaded dynamically for node, simply copies over the proto.

mkdir -p proto && \
cp ../../pb/demo.proto proto
