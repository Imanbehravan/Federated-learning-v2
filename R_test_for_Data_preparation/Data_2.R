library("TCGAbiolinks")
library("SummarizedExperiment")


GDCprojects <- getGDCprojects()
TCGAbiolinks:::getProjectSummary("TCGA-BRCA")

query_TCGA <- GDCquery(
  project = "TCGA-BRCA",
  data.category = "Transcriptome Profiling",
  data.type = "Gene Expression Quantification",
  experimental.strategy = "RNA-Seq",
  workflow.type = 'STAR - Counts',
  sample.type = "Primary Tumor")

output_query <- getResults(query_TCGA)


### building specific query

query_TCGA <- GDCquery(
  project = "TCGA-BRCA",
  data.category = "Transcriptome Profiling",
  data.type = "Gene Expression Quantification",
  experimental.strategy = "RNA-Seq",
  workflow.type = 'STAR - Counts',
  barcode = c('TCGA-B6-A0RH-01A-21R-A115-07',
              'TCGA-BH-A1FU-01A-11R-A14D-07',
              'TCGA-AR-A0TX-01A-11R-A084-07',
              'TCGA-A1-A0SE-01A-11R-A084-07',
              'TCGA-OL-A5D6-01A-21R-A27Q-07',
              'TCGA-E2-A1IK-01A-11R-A144-07',
              'TCGA-AN-A0FT-01A-11R-A034-07',
              'TCGA-A2-A3KD-01A-12R-A213-07',
              'TCGA-A2-A0EO-01A-11R-A034-07',
              'TCGA-A2-A04P-01A-31R-A034-07',
              'TCGA-AC-A5EH-01A-11R-A28M-07',
              'TCGA-A7-A0DC-01B-04R-A22O-07',
              'TCGA-OK-A5Q2-01A-11R-A27Q-07',
              'TCGA-BH-A0DO-01B-11R-A12D-07',
              'TCGA-BH-A18J-01A-11R-A12D-07',
              'TCGA-BH-A1FU-11A-23R-A14D-07',
              'TCGA-BH-A1FC-11A-32R-A13Q-07',
              'TCGA-AC-A2FM-11B-32R-A19W-07',
              'TCGA-BH-A0DO-11A-22R-A12D-07',
              'TCGA-E2-A1BC-11A-32R-A12P-07',
              'TCGA-BH-A0BJ-11A-23R-A089-07',
              'TCGA-E2-A1LH-11A-22R-A14D-07',
              'TCGA-BH-A1FB-11A-33R-A13Q-07',
              'TCGA-BH-A18M-11A-33R-A12D-07',
              'TCGA-BH-A0BM-11A-12R-A089-07',
              'TCGA-E2-A153-11A-31R-A12D-07',
              'TCGA-BH-A0H5-11A-62R-A115-07',
              'TCGA-BH-A1FG-11B-12R-A13Q-07',
              'TCGA-A7-A0DB-11A-33R-A089-07',
              'TCGA-BH-A1EU-11A-23R-A137-07',
              'TCGA-E2-A15E-06A-11R-A12D-07',
              'TCGA-BH-A1ES-06A-12R-A24H-07',
              'TCGA-E2-A15K-06A-11R-A12P-07',
              'TCGA-BH-A18V-06A-11R-A213-07',
              'TCGA-BH-A1FE-06A-11R-A213-07',
              'TCGA-E2-A15A-06A-11R-A12D-07',
              'TCGA-AC-A6IX-06A-11R-A32P-07')) # parameter enforced by GDCquery

#GDCdownload(query = query_TCGA, method = "api", files.per.chunk = 100)

tcga_data <- GDCprepare(query_TCGA,summarizedExperiment = TRUE)

class(tcga_data)

saveRDS(tcga_data,file = "TCGA.rds")
tcga_data <- readRDS("TCGA.rds")
brca_matrix <- assay(tcga_data, 'fpkm_unstrand')

sedf <- tcga_data
geneslist <- sedf@rowRanges$gene_id
samplelist <- sedf@colData@listData$sample

t_data <- t(brca_matrix)

write.csv2(t_data, file = "Gene_expression_data.csv")
write.table(t_data, file = "Gene_expression_data.txt", append = FALSE, sep = " ", dec = ".",
            row.names = TRUE, col.names = TRUE)

train_data = unlist(t_data)
dim(train_data)
pcaout <- prcomp(train_data, scale. = F)

pcaoutdata <- pcaout$x

write.table(pcaoutdata, file = "Gene_expression_PCA_data.txt", append = FALSE, sep = ",", dec = ".",
            row.names = FALSE, col.names = FALSE)
write.csv2(pcaoutdata, file = "Gene_expression_PCA_data.csv")

