(TeX-add-style-hook
 "model_point_density_validation"
 (lambda ()
   (TeX-add-to-alist 'LaTeX-provided-package-options
                     '(("inputenc" "utf8") ("fontenc" "T1") ("caption" "font=scriptsize" "labelfont=scriptsize" "labelfont={color=imfblue}")))
   (add-to-list 'LaTeX-verbatim-environments-local "semiverbatim")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "href")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "hyperref")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "hyperimage")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "hyperbaseurl")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "nolinkurl")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "url")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "path")
   (add-to-list 'LaTeX-verbatim-macros-with-delims-local "path")
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
    "extrawideenumerate")
   (LaTeX-add-xcolor-definecolors
    "imfblue"))
 :latex)

