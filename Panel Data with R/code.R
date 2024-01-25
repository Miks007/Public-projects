library(foreign)
require(dplyr)

https://www.kaggle.com/code/sandhyakrishnan02/econometric-analysis-of-panel-data-using-r

setwd("C:/Users/MikolajPawlak/Documents/GitHub/Public-projects/Panel data with R")
df <- read.csv('PanelData.csv')

if (is.data.frame(df)) {Panel <- as.data.frame(df)}
names(df)
# Predictors:
# I = Airline,
# T = Year,
# Q = Output, in revenue passenger miles, index number,
# PF = Fuel price,
# LF = Load factor, the average capacity utilization of the fleet.

# Response:
# C = Total cost, in $1000

# Mass comment - Ctrl + Shift + C 
head(df)
nrow(df)
ncol(df)
nrow(na.omit(df))
summary(df)
str(df)

# Plot a bar chart for each variable
par(mfrow = c(1, 5))  # Set up a 1x5 grid for 5 variables

for (col in names(df)) {
  if (is.numeric(df[[col]])) {
    hist(df[[col]], xlab = col, main = col, col = "skyblue", border = "black")
  }
}


# we have full panel data - 6 firms in 15 differnt times
# we can also run table(df['I'])
data %>% count(I)

corr <- cor(data)
corr
par(mfrow = c(1, 1))
corrplot::corrplot(
  corr,
  method = "square",  # Display correlation values
  type = "lower",     # Display only the lower triangle of the matrix
  addCoef.col = "black",  # Set color for correlation values
  tl.col = "black",    # Set color for variable names
  diag = FALSE         # Do not display values on the diagonal
)

# Strong correlation patterns are observed
# Variables C and G exhibit a strong negative correlation with I.
# Additionally, variables PF and T, as well as C and Q, demonstrate strong positive correlations.

library(gplots)
plotmeans(C ~ I, main="Heterogeineity across Airlines", data=df)

plotmeans(C ~ T, main="Heterogeineity across years", data=df)


##############################
############### ADD MORE VISUALIZATIONS HERE
##############################
plot(data$Q, data$C, pch=19, xlab="Q", ylab="C")

#abline(lm(Panel$y~Panel$x1),lwd=3, col="red")






###################################
########### Regular OLS ###########
###################################

library(plm)
ols <-lm(C ~ Q+PF+LF, data=df)
summary(ols)

# each of independent variables is statisically significant
# the test on F-statistic also shows that the model includes coefficients that are diffrent than zero

yhat <- ols$fitted

###################################
########## Fixed Effects ##########
###################################
#### 1. Using Least squares dummy variable (LSDV) modelSSS
fixed.dum <-lm(C ~ Q+PF+LF+factor(I)-1, data =df)
summary(fixed.dum)
# two firms (2 and 3) are statistically insignificant from 0

yhat<- fixed.dum$fitted
yhat

library(car)
Airline<-df$I
scatterplot(yhat~ df$T| Airline, xlab= "I", ylab ="yhat", boxplots = FALSE, smooth = FALSE)
abline(lm(df$C~df$T),lwd=3,col="red")

### COMPARe OLS vs LSDV model
# library(apsrtable) ## CANT INSTAL ??
# apsrtable(ols,fixed.dum, model.names = c("OLS", "OLS_DUM")) # Displays a table in Latex form

fixed <- plm(C ~ Q+PF+LF,data =df,model ="within")
summary(fixed)

fixef(fixed) # Display the fixed effects (constants for each country)
pFtest(fixed, ols) # Testing for fixed effects, null: OLS better than fixed
# p -value is <-0.05 so we reject H0 and say that the fixed model is a better choice than the ols


###################################
########## Random Effects #########
###################################
random <- plm(C ~ Q+PF+LF, data=df, index=c("I", "T"), model="random")
summary(random)
# all individual effects (Q, PF and LF) and the model are statistically significant
# R - squared: 0.91129
# Adj. R - Squared: 0.9082

###################################
########## Hausman Test ###########
###################################

# To decide between fixed or random effects we run a Hausman test 
# H0: the preferred model is RE
# H1: the preferred model is FE
phtest(fixed, random)
# p-value is lower than 0.05, so the Fixed Effects model is an appropriate estimator
# that means that random effects are probably correlated with Xit


###################################
####### Breusch-Pagan Test ########
###################################
# Heteroscedasticity

# A test to detect if the variance is not constant and increases as the predictor rises.
# If that's the case we can still depend on unbiased coefficnet but the std. err. cannot be trusted.
lmMod <- lm(C ~ Q+PF+LF+factor(I)+factor(T), data=df)
plot(lmMod)
# The plots we are interested in are residuals vs fitted values and standardised residuals on Y axis. 
# If there is absolutely no heteroscedastity, you should see a completely random, 
# equal distribution of points throughout the range of X axis and a flat red line.

# But in our case, as you can notice from the residuals vs fitted values plot, 
# the red line is slightly curved and the residuals seem to increase as the 
# fitted Y values increase. So, the inference here is, heteroscedasticity exists.


bptest(C ~ Q+PF+LF+factor(I)+factor(T), data=df, studentize=F)
# As the P-value of the BP test is less than 5%, 
# indicates the variance is changing in the residual as the predictor value increases, 
# thus we can reject the null hypothesis. Therefore, the data has heteroscedasticity.
install.packages("cli", version = "3.6.1", dependencies = TRUE)
detach("package:caret", unload = TRUE)
library(caret)

distBCMod <- caret::BoxCoxTrans(df$C)
print(distBCMod)

df <- cbind(df, C_new=predict(distBCMod, df$C)) 
head(df)

library(lmtest)
lmMod_bc <- lm(C_new ~ Q+PF+LF+factor(I)+factor(T), data=df)
bptest(lmMod_bc)
plot(lmMod_bc)

# Now after Box-Cox transformation, residuals vs fitted values plot have a much flatter line

# original coefficient
library(lmtest)
library(plm)
coeftest(fixed)

# vcovHC() is used for heteroscedasticity-consistent estimation of the covariance matrix of the coefficient estimates in regression models.
coeftest(fixed, vcovHC)


coeftest(fixed, vcovHC(fixed, method = "arellano"))



#### DOKOŃCZ !!!!!!!!!!!!!!!!!!!!!!!!!!
