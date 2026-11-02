# VHS tape script for recording laravel-spec-skill 10-second demo
# Prerequisites: Install vhs (https://github.com/charmbracelet/vhs)
# Usage: vhs demo.tape

Output demo.gif

Set FontSize 14
Set Width 1200
Set Height 680
Set Theme "Catppuccin Mocha"
Set WindowBar Colorful

Type "python scripts/validate_spec.py examples/marketplace/spec.json --strict"
Sleep 500ms
Enter
Sleep 3s

Type "python scripts/render_docs.py examples/marketplace/spec.json --output-dir demo-output/docs"
Sleep 500ms
Enter
Sleep 2s

Type "python scripts/render_commands.py examples/marketplace/spec.json --output demo-output/commands.sh"
Sleep 500ms
Enter
Sleep 2s

Type "head -n 25 demo-output/commands.sh"
Sleep 500ms
Enter
Sleep 3s
