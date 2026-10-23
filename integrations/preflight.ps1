# Contrôle local facultatif, pas un hook automatiquement installé.
$ErrorActionPreference = 'Stop'
python tools/check_policy.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python tools/verify.py --profile full
exit $LASTEXITCODE
