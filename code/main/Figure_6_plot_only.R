
rm(list = ls())
source(file.path(dirname(normalizePath(sub("^--file=", "", commandArgs(trailingOnly=FALSE)[grep("^--file=", commandArgs(trailingOnly=FALSE))]), winslash="/")), "_paths_and_note.R"))

required_packages <- c("ggplot2","dplyr","tidyr","cowplot","grid")
missing <- required_packages[!vapply(required_packages, requireNamespace, logical(1), quietly=TRUE)]
if (length(missing)) stop("Missing R package(s): ", paste(missing, collapse=", "))
suppressPackageStartupMessages({
  library(ggplot2); library(dplyr); library(tidyr); library(cowplot); library(grid)
})

dat <- read.csv(file.path(data_dir,"figure6_plot_data.csv"),stringsAsFactors=FALSE,check.names=FALSE)

get_value <- function(panel_id, group_id, metric_id) {
  x <- dat %>%
    filter(
      .data$panel == .env$panel_id,
      .data$group == .env$group_id,
      .data$metric == .env$metric_id
    )
  if (nrow(x) != 1) {
    stop(
      "Expected one Figure 6 value: ",
      panel_id, " / ", group_id, " / ", metric_id,
      "; found ", nrow(x)
    )
  }
  as.numeric(x$value[[1]])
}

color_rrpv <- "#FF6B35"; color_rrpv_bs <- "#004E89"
color_export <- "#F4A261"; color_savings <- "#2A9D8F"
color_gross <- "#E76F51"; color_net <- "#264653"
color_achieved <- "#457B9D"
label_size_unified <- 6.5

my_custom_theme <- theme_minimal(base_size=20) +
  theme(
    panel.background=element_rect(fill="white",colour=NA),
    plot.background=element_rect(fill="white",colour=NA),
    axis.text=element_text(size=16,face="plain",colour="black"),
    axis.title=element_text(size=18,face="plain",colour="black"),
    axis.line=element_line(linewidth=0.6,colour="black"),
    axis.ticks=element_line(linewidth=0.6,colour="black"),
    axis.ticks.length=unit(0.2,"cm"),
    panel.grid.major=element_blank(),panel.grid.minor=element_blank(),
    axis.text.x=element_text(angle=0,hjust=0.5,vjust=0.5,margin=margin(t=6)),
    axis.text.y=element_text(margin=margin(r=6)),
    plot.margin=margin(t=12,r=12,b=12,l=12),
    legend.position="bottom",
    legend.title=element_text(size=18,face="plain",colour="black"),
    legend.text=element_text(size=16,face="plain",colour="black"),
    legend.background=element_rect(fill="white",colour=NA),
    legend.key=element_rect(fill="white",colour=NA),
    plot.title=element_text(hjust=0.5,face="plain",size=22,colour="black"),
    strip.text=element_text(size=18,face="plain",colour="black")
  )

# a
df_a <- data.frame(
  System=c("RRPV-only Adopters","RRPV-BS Adopters"),
  Gross_Return_Per_kWp=c(get_value("a","RRPV-only","Gross return"),get_value("a","RRPV-BS","Gross return")),
  Net_Return_Per_kWp=c(get_value("a","RRPV-only","Net return"),get_value("a","RRPV-BS","Net return"))
) %>%
  pivot_longer(cols=c(Gross_Return_Per_kWp,Net_Return_Per_kWp),names_to="Return_Type",values_to="Value") %>%
  mutate(Return_Type=factor(Return_Type,
         levels=c("Gross_Return_Per_kWp","Net_Return_Per_kWp"),
         labels=c("Gross Return","Net Return")),
         System=factor(System,levels=c("RRPV-only Adopters","RRPV-BS Adopters")))

plot_a <- ggplot(df_a,aes(x=System,y=Value,fill=Return_Type)) +
  geom_col(position=position_dodge(width=0.7),width=0.6) +
  geom_text(aes(label=Value),position=position_dodge(width=0.7),vjust=-0.5,size=label_size_unified) +
  scale_fill_manual(values=c("Gross Return"=color_gross,"Net Return"=color_net),name="Return Type") +
  scale_y_continuous(limits=c(0,130),breaks=c(0,25,50,75,100,125),expand=expansion(mult=c(0,0.06))) +
  labs(title="Equivalent Annualized Returns",x=NULL,y="Return (US$ per kWp per year)") +
  my_custom_theme

# b
df_b <- data.frame(
  System=c("RRPV-only Adopters","RRPV-only Adopters","RRPV-BS Adopters","RRPV-BS Adopters"),
  Component=c("Export Revenue","Bill Savings","Export Revenue","Bill Savings"),
  Percentage=c(get_value("b","RRPV-only","Export revenue share"),get_value("b","RRPV-only","Bill-saving share"),
               get_value("b","RRPV-BS","Export revenue share"),get_value("b","RRPV-BS","Bill-saving share"))
) %>%
  mutate(System=factor(System,levels=c("RRPV-only Adopters","RRPV-BS Adopters")),
         Component=factor(Component,levels=c("Export Revenue","Bill Savings")))

plot_b <- ggplot(df_b,aes(x=System,y=Percentage,fill=Component)) +
  geom_col(position=position_dodge(width=0.7),width=0.6) +
  geom_text(aes(label=paste0(Percentage,"%")),position=position_dodge(width=0.7),
            vjust=-0.5,size=label_size_unified) +
  scale_fill_manual(values=c("Export Revenue"=color_export,"Bill Savings"=color_savings),
                    name="Gross-Return Component") +
  scale_y_continuous(limits=c(0,100),breaks=c(0,25,50,75,100),expand=expansion(mult=c(0,0.04))) +
  labs(title="Gross-Return Composition",x=NULL,y="Share of gross return (%)") +
  my_custom_theme

# c
df_c <- data.frame(
  Metric=c(rep("Self-Sufficiency",2),rep("Economic Viability",2)),
  System=rep(c("RRPV-only Adopters","RRPV-BS Adopters"),2),
  Percentage=c(get_value("c","RRPV-only","Self-sufficiency"),
               get_value("c","RRPV-BS","Self-sufficiency"),
               get_value("c","RRPV-only","Economic viability"),
               get_value("c","RRPV-BS","Economic viability"))
) %>% mutate(
  System=factor(System,levels=c("RRPV-only Adopters","RRPV-BS Adopters")),
  Metric=factor(Metric,levels=c("Self-Sufficiency","Economic Viability"))
)

plot_c <- ggplot(df_c,aes(x=System,y=Percentage)) +
  geom_col(fill=color_achieved,width=0.6) +
  geom_text(aes(label=paste0(Percentage,"%")),vjust=-0.5,size=label_size_unified) +
  facet_wrap(~Metric,ncol=2,strip.position="bottom") +
  scale_y_continuous(limits=c(0,100),breaks=c(0,25,50,75,100),expand=expansion(mult=c(0,0.04))) +
  labs(title="Self-Sufficiency and Economic Viability",x=NULL,y="Percentage (%)") +
  my_custom_theme +
  theme(legend.position="none",strip.text=element_text(size=16),
        strip.placement="outside",strip.background=element_blank(),
        panel.spacing=unit(1.5,"lines"),axis.text.x=element_text(size=12),
        plot.margin=margin(t=12,r=12,b=35,l=12))

make_zone <- function(panel) {
  zones <- c("Cool","Mild","Hot")
  data.frame(
    Climate_Zone=factor(zones,levels=zones),
    Export_Revenue=sapply(zones,function(z)get_value(panel,z,"Export component")),
    Bill_Savings=sapply(zones,function(z)get_value(panel,z,"Bill-saving component"))
  ) %>% mutate(Total=Export_Revenue+Bill_Savings) %>%
    pivot_longer(cols=c(Export_Revenue,Bill_Savings),names_to="Component",values_to="Value") %>%
    mutate(Component=factor(Component,levels=c("Export_Revenue","Bill_Savings"),
                            labels=c("Export Revenue","Bill Savings")))
}

df_d <- make_zone("d")
plot_d <- ggplot(df_d,aes(x=Climate_Zone,y=Value,fill=Component)) +
  geom_col(position="stack",width=0.6) +
  geom_text(aes(label=sprintf("%.1f",Value)),position=position_stack(vjust=0.5),
            size=label_size_unified,colour="white") +
  geom_text(data=df_d %>% select(Climate_Zone,Total) %>% distinct(),
            aes(x=Climate_Zone,y=Total,label=sprintf("%.0f",Total)),
            vjust=-0.5,size=label_size_unified,inherit.aes=FALSE) +
  scale_fill_manual(values=c("Export Revenue"=color_export,"Bill Savings"=color_savings),
                    name="Gross-Return Component") +
  scale_y_continuous(limits=c(0,140),breaks=c(0,25,50,75,100,125),expand=expansion(mult=c(0,0.06))) +
  labs(title="RRPV-only Adopters - Return by Climate Zone",
       x="Climate Zone",y="Gross return (US$ per kWp per year)") +
  my_custom_theme

df_e <- make_zone("e")
plot_e <- ggplot(df_e,aes(x=Climate_Zone,y=Value,fill=Component)) +
  geom_col(position="stack",width=0.6) +
  geom_text(aes(label=sprintf("%.1f",Value)),position=position_stack(vjust=0.5),
            size=label_size_unified,colour="white") +
  geom_text(data=df_e %>% select(Climate_Zone,Total) %>% distinct(),
            aes(x=Climate_Zone,y=Total,label=sprintf("%.0f",Total)),
            vjust=-0.5,size=label_size_unified,inherit.aes=FALSE) +
  scale_fill_manual(values=c("Export Revenue"=color_export,"Bill Savings"=color_savings),
                    name="Gross-Return Component") +
  scale_y_continuous(limits=c(0,140),breaks=c(0,25,50,75,100,125),expand=expansion(mult=c(0,0.06))) +
  labs(title="RRPV-BS Adopters - Return by Climate Zone",
       x="Climate Zone",y="Gross return (US$ per kWp per year)") +
  my_custom_theme

zones <- c("Cool","Mild","Hot")
df_f <- data.frame(
  System=c(rep("RRPV-only Adopters",3),rep("RRPV-BS Adopters",3)),
  Climate_Zone=rep(zones,2),
  Self_Sufficiency=c(
    sapply(zones,function(z)get_value("f",z,"RRPV-only self-sufficiency")),
    sapply(zones,function(z)get_value("f",z,"RRPV-BS self-sufficiency"))
  )
) %>% mutate(
  System=factor(System,levels=c("RRPV-only Adopters","RRPV-BS Adopters")),
  Climate_Zone=factor(Climate_Zone,levels=zones)
)

plot_f <- ggplot(df_f,aes(x=Climate_Zone,y=Self_Sufficiency,fill=System)) +
  geom_col(position=position_dodge(width=0.7),width=0.6) +
  geom_text(aes(label=paste0(Self_Sufficiency,"%"),group=System),
            position=position_dodge(width=0.7),vjust=-0.5,size=label_size_unified) +
  scale_fill_manual(values=c("RRPV-only Adopters"=color_rrpv,"RRPV-BS Adopters"=color_rrpv_bs),
                    name="System Type") +
  scale_y_continuous(limits=c(0,110),breaks=c(0,25,50,75,100),expand=expansion(mult=c(0,0.06))) +
  labs(title="Self-Sufficiency by Climate Zone",x="Climate Zone",y="Self-Sufficiency (%)") +
  my_custom_theme

final_plot <- plot_grid(plot_a,plot_b,plot_c,plot_d,plot_e,plot_f,
                        labels=c("a","b","c","d","e","f"),label_size=24,
                        ncol=3,align="hv",axis="lr")

ggsave(file.path(output_dir,"Figure_6.pdf"),final_plot,width=24,height=16,device=cairo_pdf,bg="white",limitsize=FALSE)
ggsave(file.path(output_dir,"Figure_6.png"),final_plot,width=24,height=16,dpi=300,bg="white",limitsize=FALSE)
message("Figure 6 reproduced successfully.")
