#!/usr/bin/env bash
# Garimpa issues de entrada nos projetos do seu stack.
#
# Não abre PR nem contribui por você: só reduz o tempo de ACHAR uma issue boa,
# que é onde a maior parte do esforço se perde. A escolha e o código continuam seus.
#
#   bash scripts/find-issues.sh            # issues de entrada, sem responsável
#   bash scripts/find-issues.sh --all      # inclui issues já atribuídas
#   bash scripts/find-issues.sh --docs     # só documentação e tradução

set -uo pipefail

# Repositórios do stack. Edite à vontade: quanto mais próximo do que você já usa,
# maior a chance de você resolver rápido e o mantenedor aceitar.
REPOS=(
  microsoft/TypeScript  vitejs/vite          vitest-dev/vitest
  vercel/next.js        facebook/react       tailwindlabs/tailwindcss
  laravel/framework     symfony/symfony      filamentphp/filament
  livewire/livewire     phpstan/phpstan      nodejs/node
  honojs/hono           prettier/prettier    typescript-eslint/typescript-eslint
  drizzle-team/drizzle-orm                   neo4j/neo4j
)

# Os nomes de label mudam de projeto para projeto (o TypeScript usa maiúsculas,
# o Laravel só tem "help wanted"), por isso varremos as variações.
LABELS=("good first issue" "Good First Issue" "help wanted" "help-wanted" "E-easy")
[[ "${1:-}" == "--docs" ]] && LABELS=("documentation" "Documentation" "docs" "needs documentation")

SO_SEM_DONO=true
[[ "${1:-}" == "--all" ]] && SO_SEM_DONO=false

command -v gh >/dev/null || { echo "gh não encontrado"; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "gh não autenticado"; exit 1; }

ARGS=()
for r in "${REPOS[@]}"; do ARGS+=(--repo "$r"); done

TMP=$(mktemp); trap 'rm -f "$TMP"' EXIT

echo "Procurando em ${#REPOS[@]} repositórios..."
for L in "${LABELS[@]}"; do
  gh search issues "${ARGS[@]}" --label "$L" --state open --limit 40 \
     --json repository,title,url,createdAt,assignees,commentsCount 2>/dev/null \
    | python3 -c '
import json, sys
try:
    dados = json.load(sys.stdin)
except Exception:
    sys.exit()
for i in dados:
    print("\t".join([
        i["repository"]["nameWithOwner"], i["title"].replace("\t", " "),
        i["url"], i["createdAt"][:10],
        str(len(i.get("assignees") or [])), str(i.get("commentsCount", 0)),
    ]))' >> "$TMP"
done

# no maximo 3 por repositorio: sem isso um projeto que abre dezenas de issues
# no mesmo dia (o Symfony faz isso com traducoes) toma a lista inteira
sort -u "$TMP" | awk -F'\t' -v filtrar="$SO_SEM_DONO" '
  filtrar == "true" && $5 != "0" { next }
  { print }
' | sort -t$'\t' -k4,4r | awk -F'\t' '
  { if (vistos[$1]++ < 3) print }
' | head -20 | awk -F'\t' '
  BEGIN { printf "\n%-26s  %-58s  %-10s  %s\n", "REPOSITÓRIO", "ISSUE", "ABERTA EM", "COMENTÁRIOS" 
          printf "%s\n", "-------------------------------------------------------------------------------------------------------------" }
  { t = length($2) > 56 ? substr($2, 1, 55) "…" : $2
    printf "%-26s  %-58s  %-10s  %s\n    %s\n", $1, t, $4, $6, $3 }
'

echo
echo "Dica: issue com poucos comentários e aberta há algumas semanas costuma estar"
echo "realmente livre. Muitos comentários geralmente significam que já tem alguém."
