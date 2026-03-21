#
# ~/.bashrc
#

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

set -o vi
bind '"jk":vi-movement-mode'

export EDITOR="nvim"

alias ls="lsd"
alias ll="ls --long --header"
alias grep='grep --color=auto'
alias performance="powerprofilesctl set performance"
alias balanced="powerprofilesctl set balanced"
alias power-saver="powerprofilesctl set power-saver"
alias powerls="powerprofilesctl"
alias update-grub="sudo grub-mkconfig -o /boot/grub/grub.cfg"
alias nvdir="nvim \$(fd -t d -E 'Games' | fzf --preview 'eza --icons --color=always --long --header {}')"
PS1='[\u@\h \W]\$ '

eval "$(zoxide init bash)"
# eval "$(/bin/brew shellenv)"
# Set up fzf key bindings and fuzzy completion
eval "$(fzf --bash)"
export PATH=$PATH:/home/inshaal/.local/bin
eval "$(oh-my-posh init bash --config ~/.cache/oh-my-posh/themes/half-life.omp.json)"
