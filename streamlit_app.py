
import streamlit as st
import pandas as pd
import plotly.express as px

# Sayfa genişliği artırıldı
st.set_page_config(layout="wide")


st.title("Üretim Gerçekleşen Paneli")

password = st.text_input("Parola girin", type="password")

if password:
    if password == "ketsan123":
        st.success("Giriş başarılı!")

# csv dosyasını yükle
        dosya_adi = "uretimgerc.csv"
        df_all = pd.read_csv(dosya_adi)
        df = df_all
        df["TARIH"] = pd.to_datetime(df["TARIH"])
        

    # Filtreler
        tezgah = st.sidebar.multiselect("Grup Kodu", df["KOD1"].unique())
        bolum = st.sidebar.multiselect("Bölüm", df["BOLUM"].unique())
        tarih_araligi = st.sidebar.date_input(
            "Tarih Aralığı",
            [df["TARIH"].min().date(), df["TARIH"].max().date()]
        )

#####

        filtered_df = df.copy()

#####

        if tezgah:
            filtered_df = filtered_df[filtered_df["KOD1"].isin(tezgah)]
        if bolum:
            filtered_df = filtered_df[filtered_df["BOLUM"].isin(bolum)]
        if len(tarih_araligi) == 2:
            start_date, end_date = tarih_araligi
            filtered_df = filtered_df[(filtered_df["TARIH"] >= pd.to_datetime(start_date)) & 
                                        (filtered_df["TARIH"] <= pd.to_datetime(end_date))]
    
#Line chart

        filtered_df["TARIH"] = filtered_df["TARIH"].dt.normalize()

        durus_line = filtered_df.groupby("TARIH")["SONOPERASYON_MIKTAR"].sum().reset_index
        durus_line = durus_line ()
        durus_line ["TARIH"] = pd.to_datetime(durus_line ["TARIH"])
        durus_line ["TARIH_STR"] = durus_line ["TARIH"].dt.strftime("%d %B")
        fig = px.line(durus_line , x="TARIH", y= "SONOPERASYON_MIKTAR")
        st.plotly_chart(fig)

  
        df_grup2 = filtered_df.groupby("URUN_ADI")["SONOPERASYON_MIKTAR"].sum().reset_index()
        df_grup2["SONOPERASYON_MIKTAR"] = df_grup2["SONOPERASYON_MIKTAR"].round(0).astype(int)
        df_grup2.columns = ["Ürün", "Üretilen Adet"]


#Pie chart

        if "TALASLI_IMALAT" in bolum:  # bolum, sidebar'dan seçtiğin liste ise
            uretimadet_pie = filtered_df.groupby("KOD1")["SONOPERASYON_MIKTAR"].sum().round(0).reset_index()
            fig1 = px.pie(uretimadet_pie, values="SONOPERASYON_MIKTAR", names="KOD1", title="Ürün Grubu Bazında Üretilen Adet")

        elif "DOVME" in bolum:
            uretimadet_pie = filtered_df.groupby("TEZGAHISIM")["SONOPERASYON_MIKTAR"].sum().round(0).reset_index()
            fig1 = px.pie(uretimadet_pie, values="SONOPERASYON_MIKTAR", names="TEZGAHISIM", title="Pres Bazında Üretilen Adet")
        
        else:
            fig1 = px.pie()

    # BAR CHART - AGIRLIK
        if "DOVME" in bolum: 
            agirlik_df = filtered_df.groupby("TEZGAHISIM")["GERCEKLESEN_TONAJ"].sum().round(0).reset_index()
            fig3 = px.bar(agirlik_df, x="TEZGAHISIM", y="GERCEKLESEN_TONAJ", title="Pres Bazında Gerçekleşen Tonaj",
                  labels={"GERCEKLESEN_TONAJ": "Toplam Ağırlık (kg)", "TEZGAHISIM": "Makine"},
                  text="GERCEKLESEN_TONAJ")
            fig3.update_traces(textposition='outside')
        
        else:
            fig3 = px.pie()
        
           
        fig1.update_layout(
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.2,
                xanchor="right",
                x=0.8
            )
        )


# urun bazlı bar chart
        durus_urun = filtered_df.groupby(["URUN_KODU"])["SONOPERASYON_MIKTAR"].sum().round(0).reset_index()

        fig2 = px.bar(
            durus_urun,
            x="URUN_KODU",
            y="SONOPERASYON_MIKTAR",
            hover_data=["URUN_KODU"],  # Tooltip içine ürün adı
        )
        fig2.update_traces(textposition='outside')


        col1, col2 = st.columns(2)  # 2 kolon oluşturduk

        with col1:
            st.plotly_chart(fig1, use_container_width=True)  # use_container_width genişliği kolon genişliğine uyarlar

        with col2:
            st.plotly_chart(fig3, use_container_width=True)
        
        #ortalama durus uresi
        st.plotly_chart(fig2, use_container_width=True)

# Boşluk
        st.sidebar.markdown("<br><br>", unsafe_allow_html=True)

# Özet
        st.sidebar.markdown("### ÜRETİM PERFORMANS ÖZET")
        if not filtered_df.empty:
            toplam_uretilen = filtered_df["SONOPERASYON_MIKTAR"].sum()
            hedef = 0
            gerceklesen_yuzde = toplam_uretilen/hedef
            gerceklesen_yuzde = round(gerceklesen_yuzde, 2)

            st.sidebar.write(f"Toplam Üretim Adedi: {toplam_uretilen}")
            st.sidebar.write(f"Hedef Adet: {hedef}")
            st.sidebar.write(f"Gerçekleşen Adet(%) : % ")
    
        else:
            st.sidebar.write("Seçilen filtrelerde veri yok.")

    else:
        st.error("Parola yanlış")
