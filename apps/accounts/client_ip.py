"""Explicit proxy boundary without Uvicorn rewriting the original peer."""

import ipaddress


def trusted_networks(cidrs: tuple[str, ...]):
    networks = []
    try:
        for cidr in cidrs:
            network = ipaddress.ip_network(cidr, strict=True)
            if network.prefixlen == 0:
                raise ValueError
            networks.append(network)
    except (ValueError, TypeError):
        raise ValueError("invalid trusted proxy configuration") from None
    return tuple(networks)


def _address(raw: str):
    if not isinstance(raw, str) or len(raw) > 45 or "%" in raw:
        raise ValueError("invalid client address")
    try:
        address = ipaddress.ip_address(raw)
    except ValueError:
        raise ValueError("invalid client address") from None
    if isinstance(address, ipaddress.IPv6Address) and address.ipv4_mapped:
        return address.ipv4_mapped
    return address


def client_ip(
    peer: str, forwarded_for: str | None, trusted_cidrs: tuple[str, ...]
) -> str:
    address = _address(peer)
    networks = trusted_networks(trusted_cidrs)
    if not any(address in network for network in networks) or forwarded_for is None:
        return str(address)
    if len(forwarded_for) > 512:
        raise ValueError("invalid forwarded chain")
    hops = forwarded_for.split(",")
    if not 1 <= len(hops) <= 10:
        raise ValueError("invalid forwarded chain")
    chain = [_address(hop.strip()) for hop in hops]
    for candidate in reversed(chain):
        if not any(address in network for network in networks):
            break
        address = candidate
    return str(address)
