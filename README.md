# Mockr

```sh
# Automatic optimization (recommended)
uv run mockr --fast

# For CPU-intensive applications
# Rule: processes = CPU cores, workers = 1
# Example: 8-core machine
uv run mockr --processes 8 --workers 1

# For I/O-intensive applications  
# Rule: processes = CPU cores / 2, workers = 2-4
# Example: 8-core machine
uv run mockr  --processes 4 --workers 3

# For balanced applications
# Rule: processes = CPU cores / 2, workers = 2
# Example: 8-core machine
uv run mockr --processes 4 --workers 2

# Memory considerations
# Each process uses ~50-100MB base memory
# Monitor with: ps aux | grep python
```