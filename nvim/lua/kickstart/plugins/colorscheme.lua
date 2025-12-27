return {
    "pkazmier/neovim-ayu",
    priority = 1000, -- Make sure to load this before all the other start plugins.
    config = function()
        vim.cmd.colorscheme "ayu-dark"
    end,
}
