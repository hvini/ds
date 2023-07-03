install.packages("dplyr")
install.packages("gplots")
install.packages("FSA")

path <- "/Users/vinicius/Documents/db"

setwd(path)

data <- read.csv("insurance.csv")

# primeiras cinco linhas do dataset
head(data, 5)

# estrutura do dataset
str(data)

# informações sobre o dataset
summary(data)

library("dplyr")

# renomeia colunas para facilitar o entendimento
renamed_df <- data %>%
    rename(
        "idade" = "age",
        "genero" = "sex",
        "imc" = "bmi",
        "filhos" = "children",
        "fumante" = "smoker",
        "regiao" = "region",
        "custo" = "charges"
    )

head(renamed_df, 5)

# renomeia genero para masculino e feminino
renamed_df$genero <- recode(renamed_df$genero,
    male = "masculino",
    female = "feminino"
)

# renomeia fumante para sim e não
renamed_df$fumante <- recode(renamed_df$fumante,
    yes = "sim",
    no = "não"
)

# renomeia regiao para nordeste, sudeste, sudoeste e noroeste
renamed_df$regiao <- recode(renamed_df$regiao,
    northeast = "nordeste",
    southeast = "sudeste", southwest = "sudoeste", northwest = "noroeste"
)

head(renamed_df, 5)

boxplot(renamed_df$idade, main = "Idade", ylab = "Idade")
boxplot(renamed_df$imc, main = "IMC", ylab = "IMC")
boxplot(renamed_df$filhos, main = "Filhos", ylab = "Filhos")
boxplot(renamed_df$custo, main = "Custo", ylab = "Custo")

barplot(table(renamed_df$genero), main = "Gênero", ylab = "Quantidade")
barplot(table(renamed_df$fumante), main = "Fumante", ylab = "Quantidade")
barplot(table(renamed_df$regiao), main = "Região", ylab = "Quantidade")

colSums(is.na(renamed_df))

unique_values <- lapply(renamed_df[c("genero", "fumante", "regiao")], unique)
unique_values

boxplot(custo ~ genero,
    data = renamed_df, main = "Custo por gênero", ylab = "Custo"
)

table(renamed_df$genero)

boxplot(custo ~ fumante,
    data = renamed_df, main = "Custo por fumante", ylab = "Custo"
)

table(renamed_df$fumante)

boxplot(custo ~ regiao,
    data = renamed_df, main = "Custo por região", ylab = "Custo"
)

table(renamed_df$regiao)

boxplot(custo ~ filhos,
    data = renamed_df, main = "Custo por filhos", ylab = "Custo"
)

table(renamed_df$filhos)

# regressão linear

# converte variáveis categóricas para numéricas
numeric_df <- renamed_df
numeric_df$genero <- ifelse(numeric_df$genero == "masculino", 1, 0)
numeric_df$fumante <- ifelse(numeric_df$fumante == "sim", 1, 0)
numeric_df$regiao <- as.numeric(factor(numeric_df$regiao,
    levels = unique(numeric_df$regiao)
))

head(numeric_df, 5)

correlation_matrix <- cor(numeric_df)
correlation_matrix

library("gplots")

heatmap.2(correlation_matrix,
    main = "Correlation Heatmap",
    col = colorRampPalette(c("white", "grey"))(100),
    key = FALSE,
    symkey = FALSE,
    trace = "none",
    cexCol = 1.3,
    cexRow = 1.3,
    srtCol = 45,
    cellnote = round(correlation_matrix, 2),
    notecol = "white",
    notecex = 1
)

model1 <- lm(custo ~ idade, numeric_df)
summary(model1)

model2 <- lm(custo ~ idade + genero, numeric_df)
summary(model2)

model3 <- lm(custo ~ idade + genero + imc, numeric_df)
summary(model3)

model4 <- lm(custo ~ idade + genero + imc + filhos, numeric_df)
summary(model4)

model5 <- lm(custo ~ idade + genero + imc + filhos + fumante, numeric_df)
summary(model5)

model6 <- lm(custo ~ idade + imc + filhos + fumante, numeric_df)
summary(model6)

model7 <- lm(custo ~ fumante, numeric_df)
summary(model7)

# anova

# divide o dataset em fumantes e não fumantes
fumantes <- renamed_df %>%
    filter(fumante == "sim")

nao_fumantes <- renamed_df %>%
    filter(fumante == "não")

# teste de normalidade
shapiro.test(fumantes$custo)
shapiro.test(nao_fumantes$custo)

# rejeita hipotese nula
# h0 = custo é normalmente distribuido
kruskal.test(custo ~ regiao, data = fumantes)
kruskal.test(custo ~ regiao, data = nao_fumantes)

# rejeita hipotese nula
# h0 = custo medio é igual para todas as regiões

library("dunn.test")

# teste de dunn
dunn.test(fumantes$custo, fumantes$regiao, method = "bonferroni")
dunn.test(nao_fumantes$custo, nao_fumantes$regiao, method = "bonferroni")

# calcula diferença custo medio entre nordeste sudeste para fumantes
mean(fumantes$custo[fumantes$regiao == "nordeste"]) -
    mean(fumantes$custo[fumantes$regiao == "sudeste"])

# calcula diferença custo medio entre nordeste sudeste para não fumantes
mean(nao_fumantes$custo[nao_fumantes$regiao == "nordeste"]) -
    mean(nao_fumantes$custo[nao_fumantes$regiao == "sudeste"])
