#import "@preview/nexum-apa-core:0.1.0": apa-figure

#let results-content = [
  La mezcla de guisantes con sal y agua presentó un color blanquecino. Tras el filtrado se obtuvo un líquido verde oscuro, como se muestra en @fig:filtrado.

  Al añadir el jabón líquido no se formó espuma y, después de 10 minutos de reposo, el líquido presentó un aspecto viscoso y un color verde intenso.

  Después de añadir el alcohol frío apareció material blanquecino en la zona de transición, como se observa en @fig:precipitacion. Se recogió una pequeña cantidad de filamentos.

  #apa-figure(
    image("../figures/figure-1-placeholder.svg", width: 42%),
    title: [Líquido obtenido después de la filtración],
    note: [Imagen ilustrativa de reemplazo; sustituir por la fotografía de la práctica.],
    alt: "Imagen provisional del filtrado vegetal",
  ) <fig:filtrado>

  #apa-figure(
    image("../figures/figure-2-placeholder.svg", width: 42%),
    title: [Precipitación de material en la capa de alcohol],
    note: [Imagen ilustrativa de reemplazo; sustituir por la fotografía de la práctica.],
    alt: "Imagen provisional de la precipitación",
  ) <fig:precipitacion>
]
