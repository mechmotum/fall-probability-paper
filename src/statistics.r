library(lme4)
library(readxl)
library(tidyverse)
library(effects)
library(jtools)
library(ggeffects)
library(ggplot2)

data_path_6 <- "./data/all_perturbations_6kmh.csv"
data_path_10 <- "./data/all_perturbations_10kmh.csv"

for (i in 1:2) {
  if (i == 1) {
    data <- read.csv(data_path_6)
  } else {
    data <- read.csv(data_path_10)
  }

  data$balance_assist <- as.factor(data$balance_assist)

  model_simple <- glm(
      formula = fall ~ X + angular_impulse + balance_assist + roll_angle + steer_angle + balance_assist:roll_angle + balance_assist:steer_angle + balance_assist:X + balance_assist:angular_impulse,
      data = data,
      family = binomial,
  )
  print(summary(model_simple))
  print(summ(model_simple, exp = TRUE))
  
  # Create dummy dataset with all variables set to zero, except for angular impulse
  # and state of balance-assist. The model created above uses this dataset to predict
  # fall probabilities and show the difference between balance-assist off and 
  # balance-assist on.
  dummy_data_on <- data.frame(
    angular_impulse = seq(from = -2.5, to = 2.5, by = 0.01)
  )
  dummy_data_on$X <- 0
  dummy_data_on$roll_angle <- 0
  dummy_data_on$steer_angle <- 0
  dummy_data_on$direction <- 0
  dummy_data_off <- dummy_data_on

  dummy_data_on$balance_assist <- as.factor(1)
  dummy_data_on$prediction <- predict(
    model_simple, dummy_data_on, type = "response"
  )
  dummy_data_off$balance_assist <- as.factor(0)
  dummy_data_off$prediction <- predict(
    model_simple, dummy_data_off, type = "response"
  )

  if (i == 1) {
    file_name <- "./figures/predicted_fall_probability_6kmh.png"
  } else {
    file_name <- "./figures/predicted_fall_probability_10kmh.png"
  }

  plot <- ggplot() +
      geom_smooth(
          data = dummy_data_on,
          linetype = 'twodash',
          aes(x = angular_impulse, y = prediction, colour = "Balance-assist on"),
          method = "glm",
          method.args = list(family = binomial),
          fill = "grey"
      ) +
      geom_smooth(
          data = dummy_data_off,
          aes(x = angular_impulse, y = prediction, colour = "Balance-assist off"),
          method = "glm",
          method.args = list(family = binomial),
          fill = "grey"
      ) +
      scale_colour_manual("",
          breaks = c("Balance-assist on", "Balance-assist off"),
          values = c("Balance-assist on" = "black",
                     "Balance-assist off" = "black")) +
      # TODO : Legend shows a solid line for each line, instead of dashed for
      # one.
      scale_linetype_manual(
          breaks = c("Balance-assist on", "Balance-assist off"),
          values = c("Balance-assist on" = "twodash",
                     "Balance-assist off" = "solid")) +
      theme_bw() +
      theme(legend.position = "bottom") +
      labs(x = "Centered and scaled angular impulse",
           y = "Fall Probability")
  ggsave(file = file_name,
         width = 80/24.5 ,
         height = 60/25.4,
         dpi = 300)
}
