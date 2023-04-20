(TeX-add-style-hook
 "conclusion"
 (lambda ()
   (TeX-add-to-alist 'LaTeX-provided-package-options
                     '(("inputenc" "utf8") ("fontenc" "T1") ("caption" "font=scriptsize" "labelfont=scriptsize" "labelfont={color=imfblue}")))
   (TeX-run-style-hooks
    "latex2e"
    "beamer"
    "beamer10"
    "inputenc"
    "fontenc"
    "lmodern"
    "amsfonts"
    "amsmath"
    "mathabx"
    "bm"
    "bbm"
    "graphicx"
    "subfig"
    "changepage"
    "xcolor"
    "booktabs"
    "rotating"
    "multirow"
    "caption"
    "import"
    "appendixnumberbeamer"
    "hyperref")
   (TeX-add-symbols
    '("blfootnote" 1))
   (LaTeX-add-environments
    "wideitemize"
    "wideenumerate"
    "extrawideitemize"
    "extrawideenumerate"))
 :latex)

