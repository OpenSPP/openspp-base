# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

{
    "name": "OpenSPP Smile Audit",
    "category": "OpenSPP",
    "version": "15.0.0.0.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/openspp/openspp-registry",
    "license": "LGPL-3",
    "development_status": "Production/Stable",
    "maintainers": ["jeremi", "gonzalesedwin1123"],
    "depends": [
        "base",
        "smile_audit",
        # "g2p_registry_base",
        # "g2p_registry_group",
        # "g2p_registry_individual",
    ],
    "external_dependencies": {},
    "data": [
        "data/audit_rules_data.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}