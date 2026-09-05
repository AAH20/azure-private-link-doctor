from __future__ import annotations


ZONE_SUFFIXES = {
    "blob.core.windows.net": "privatelink.blob.core.windows.net",
    "dfs.core.windows.net": "privatelink.dfs.core.windows.net",
    "file.core.windows.net": "privatelink.file.core.windows.net",
    "vault.azure.net": "privatelink.vaultcore.azure.net",
    "database.windows.net": "privatelink.database.windows.net",
    "postgres.database.azure.com": "privatelink.postgres.database.azure.com",
    "mysql.database.azure.com": "privatelink.mysql.database.azure.com",
    "azurewebsites.net": "privatelink.azurewebsites.net",
}


def expected_zone(fqdn: str) -> str | None:
    lowered = fqdn.lower().rstrip(".")
    matches = [(suffix, zone) for suffix, zone in ZONE_SUFFIXES.items() if lowered.endswith(suffix)]
    return max(matches, key=lambda item: len(item[0]))[1] if matches else None


def record_name(fqdn: str) -> str:
    return fqdn.split(".", 1)[0].lower()
