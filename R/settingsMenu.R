
settingsMenu_ui <- function(){
  navbarMenu(
    title = icon("gear"),  # Gear icon for settings
    tabPanel("Appearance",
             wellPanel(
               radioButtons("mode", "Mode", c("Light", "Dark")),
               sliderInput("text_size", "Text Size", min = 10, max = 30, value = 12)
             )
    ),
    tabPanel("Blender Settings",
             wellPanel(
               textInput("blenderPath", "Blender Path"),  # Removed value = paths$blender
               helpText("Paste the path of the Blender executable here.")
             )
    )
  )
}
