# Claude Code's native installer puts its binary here.
export PATH="$HOME/.local/bin:$PATH"
[[ -z "$HOMEBREW_PREFIX" && -x /opt/homebrew/bin/brew ]] && eval "$(/opt/homebrew/bin/brew shellenv zsh)"

HISTFILE="$HOME/.zsh_history"
HISTSIZE=100000
SAVEHIST=100000
setopt SHARE_HISTORY HIST_IGNORE_ALL_DUPS HIST_IGNORE_SPACE HIST_REDUCE_BLANKS
setopt AUTO_CD INTERACTIVE_COMMENTS

FPATH="$HOMEBREW_PREFIX/share/zsh/site-functions:$FPATH"
autoload -Uz compinit && compinit
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Za-z}'
zstyle ':completion:*' menu select

(( $+commands[mise] )) && eval "$(mise activate zsh)"
(( $+commands[fzf] )) && source <(fzf --zsh)
(( $+commands[starship] )) && eval "$(starship init zsh)"

if (( $+commands[eza] )); then
  alias ls="eza --group-directories-first"
  alias ll="eza -la --git --group-directories-first"
fi
alias g="git"

# zsh-syntax-highlighting must load last, after every other widget is defined.
autosuggestions="$HOMEBREW_PREFIX/share/zsh-autosuggestions/zsh-autosuggestions.zsh"
syntax_highlighting="$HOMEBREW_PREFIX/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh"
[[ -r "$autosuggestions" ]] && source "$autosuggestions"
[[ -r "$syntax_highlighting" ]] && source "$syntax_highlighting"
unset autosuggestions syntax_highlighting
