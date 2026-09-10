# Demo repositories

Create `demo-app-vulnerable` and `demo-app-clean` as separate public repositories before presenting.
The vulnerable version should contain one dependency CVE, one detectable hard-coded secret, and one Semgrep-detectable unsafe construct; verify all three tools detect the planted examples. The clean version should be the same small app with those issues removed.
