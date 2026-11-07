(module
  ;; Declareer en exporteer 3 geheugenpagina's (192 KB)
  (memory (export "memory") 3)

  ;; Sla de JSON dataset met brandstofprijzen, dagverschillen én historische trenddata op in lineair geheugen op offset 0
  (data (i32.const 0) "{\"stations\": [...], \"trends\": {\"daily\": [...], \"weekly\": [...], \"monthly\": [...], \"yearly\": [...]}}")

  ;; Exporteer functies om data-offset, datalengte en het aantal stations op te halen
  (func (export "get_data_offset") (result i32)
    i32.const 0
  )

  (func (export "get_data_len") (result i32)
    ;; Geeft de exacte lengte van de JSON-data in bytes terug
    i32.const 94670
  )

  (func (export "get_station_count") (result i32)
    ;; Geeft het totale aantal geregistreerde stations terug
    i32.const 178
  )
)
