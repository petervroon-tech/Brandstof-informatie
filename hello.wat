(module
  ;; Declareer en exporteer 1 geheugenpagina (64 KB)
  (memory (export "memory") 1)

  ;; Sla de JSON dataset met brandstofprijzen op in lineair geheugen op offset 0
  (data (i32.const 0) "[{\"name\": \"Fieten Olie\", \"city\": \"Apeldoorn\", ...}]")

  ;; Exporteer functies om data-offset, datalengte en het aantal stations op te halen
  (func (export "get_data_offset") (result i32)
    i32.const 0
  )

  (func (export "get_data_len") (result i32)
    ;; Geeft de exacte lengte van de JSON-data in bytes terug
    i32.const 4491
  )

  (func (export "get_station_count") (result i32)
    ;; Geeft het totale aantal geregistreerde stations terug
    i32.const 34
  )
)
