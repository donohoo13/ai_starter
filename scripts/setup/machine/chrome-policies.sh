#!/usr/bin/env bash
# Apply Chrome settings as user-level "Recommended" policies.
#
# Recommended policies act as defaults: Chrome starts with these values, but they
# can still be changed in chrome://settings. Every policy here was checked against
# Chrome 154 (chrome://policy shows Status "OK").
#
# Not settable this way (Chrome blocks these on Macs not enrolled in MDM, so set them by hand):
#   - On startup -> Continue where you left off      (RestoreOnStartup)
#   - Site search shortcuts, e.g. `gh` for GitHub    (SiteSearchSettings)
#   - Usage statistics / crash reports off           (MetricsReportingEnabled)
# Not policy-backed at all: "Allow Chrome sign-in", DevTools preferences.
#
# Usage:  ./chrome-policies.sh          apply
#         ./chrome-policies.sh --reset  remove every policy this script sets
# Then restart Chrome, or open chrome://policy and click "Reload policies".

set -euo pipefail

DOMAIN=com.google.Chrome

# key|type|value (array values are space-separated)
POLICIES=(
  # 1Password handles passwords, passkeys, cards, and addresses
  "PasswordManagerEnabled|bool|false"
  "AutofillCreditCardEnabled|bool|false"
  "AutofillAddressEnabled|bool|false"
  "SyncTypesListDisabled|array|passwords autofill"

  # Privacy & security
  "BlockThirdPartyCookies|bool|true"
  "HttpsOnlyMode|string|force_enabled"                  # Always use secure connections
  "SafeBrowsingProtectionLevel|int|1"                   # Standard (Enhanced sends more data to Google)
  "UrlKeyedAnonymizedDataCollectionEnabled|bool|false"  # "Make searches and browsing better"
  "DefaultNotificationsSetting|int|2"                   # Block notification prompts; allow per site

  # Efficiency
  "HighEfficiencyModeEnabled|bool|true"                 # Memory Saver
  "TabDiscardingExceptions|array|localhost 127.0.0.1"   # Never put dev servers to sleep
  "PromptForDownloadLocation|bool|true"
)

if [[ "${1:-}" == "--reset" ]]; then
  for p in "${POLICIES[@]}"; do
    defaults delete "$DOMAIN" "${p%%|*}" 2>/dev/null || true
  done
  echo "Removed Chrome policies. Restart Chrome to apply."
  exit 0
fi

for p in "${POLICIES[@]}"; do
  IFS='|' read -r key type value <<<"$p"
  if [[ "$type" == array ]]; then
    read -ra items <<<"$value"
    defaults write "$DOMAIN" "$key" -array "${items[@]}"
  else
    defaults write "$DOMAIN" "$key" "-$type" "$value"
  fi
done

echo "Applied ${#POLICIES[@]} Chrome policies. Restart Chrome or reload chrome://policy."
