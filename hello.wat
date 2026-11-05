(module
  ;; Importeer de host functie vanuit JavaScript: show_popup(pointer, lengte)
  (import "env" "show_popup" (func $show_popup (param i32 i32)))

  ;; Declareer en exporteer 1 geheugenpagina (64 KB)
  (memory (export "memory") 1)

  ;; Sla de tekst "Hello World" op in het lineaire geheugen op byte-offset 0
  (data (i32.const 0) "Hello World")

  ;; Exporteer de functie 'run' die het programma start
  (func (export "run")
    ;; Parameter 1: pointer naar begin van de tekst in het geheugen (offset 0)
    i32.const 0
    ;; Parameter 2: lengte van de tekst (11 karakters)
    i32.const 11
    ;; Roep de geïmporteerde JavaScript popup functie aan
    call $show_popup
  )
)
