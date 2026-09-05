// Review-only remediation scaffold. Supply verified resource IDs before deployment
targetScope = 'resourceGroup'

param privateDnsZoneName string
param sourceVnetId string
resource zone 'Microsoft.Network/privateDnsZones@2024-06-01' existing = { name: privateDnsZoneName }
resource link 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2024-06-01' = {
  parent: zone
  name: 'link-reviewed-source-vnet'
  location: 'global'
  properties: { registrationEnabled: false, virtualNetwork: { id: sourceVnetId } }
}
