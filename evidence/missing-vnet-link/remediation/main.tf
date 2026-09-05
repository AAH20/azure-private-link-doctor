# Review-only remediation scaffold. Do not apply without a plan and approval.

variable "private_dns_zone_name" { type = string }
variable "private_dns_zone_resource_group" { type = string }
variable "source_vnet_id" { type = string }
resource "azurerm_private_dns_zone_virtual_network_link" "reviewed" {
  name                  = "link-reviewed-source-vnet"
  resource_group_name   = var.private_dns_zone_resource_group
  private_dns_zone_name = var.private_dns_zone_name
  virtual_network_id    = var.source_vnet_id
  registration_enabled  = false
}
