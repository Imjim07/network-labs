# Network Labs

Container-based network labs built with [containerlab](https://containerlab.dev),
running real network operating systems rather than simulators.

Built while working toward CCNA and moving into network operations.

## Environment

- Windows 11 + WSL2 (Ubuntu)
- Docker + containerlab
- Nokia SR Linux

## Labs

### `first-lab/` — two-node point-to-point

Two SR Linux nodes connected over a single link, addressed in a /30,
with connectivity verified end to end.

```bash
sudo containerlab deploy -t first-lab/first-lab.clab.yml
```

The whole topology is fourteen lines of YAML. It can be destroyed and
rebuilt identically in under a minute, which is the point: the network
is a file, not a set of remembered keystrokes.

## Notes

Session logs and troubleshooting notes live in `lab-notes/`.
