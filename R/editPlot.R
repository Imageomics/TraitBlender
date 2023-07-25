

editPlot_ui <- function(){
  bsModal(id='Plot2', title='', trigger='edit_plot', size="large", backdrop='static',
          
          splitLayout(
            cellWidths = c("25%", "75%"),
            cellArgs = list(style = "padding: 6px;"),
            # This displays the code panel
            displayCodePanel_ui(),
            # This is your main content
            div(
              withSpinner(plotOutput("plot2")),
              br(),
              
              
              plotButtons_ui(),
              
              
              sortable_js("plotMenu",
                          options = sortable_options(
                            onSort = sortable_js_capture_input(input_id = "plot_elements")
                          ))
              
              
              
            )
          )
  )
}