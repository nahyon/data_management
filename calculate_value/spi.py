# SPI 계산 함수
from decimal import Decimal


def calculate_spi_cri(c, r, i, level_name="보조간선"):
    c, r, i = Decimal(c), Decimal(r), Decimal(i)
    spi1_30 = 10 - (Decimal(1.667) * (c ** Decimal(0.38))) if (10 - (
            Decimal(1.667) * (c ** Decimal(0.38)))) > 0 else 0
    spi2_30 = 10 - (Decimal(0.267) * r) if (10 - (Decimal(0.267) * r)) else 0
    if level_name == "도시고속":
        spi3_30 = 10 - Decimal(0.8) * i if 10 - Decimal(0.8) * i >= 0 else 0
    elif level_name == "보조간선":
        spi3_30 = 10 - Decimal(0.667) * i if 10 - Decimal(0.667) * i >= 0 else 0
    else:
        spi3_30 = 10 - Decimal(0.727) * i if 10 - Decimal(0.727) * i >= 0 else 0
    spi_30 = 10 - ((10 - spi1_30) ** 5 + (10 - spi2_30) ** 5 + (10 - spi3_30) ** 5) ** Decimal(0.2) if 10 - (
            (10 - spi1_30) ** 5 + (10 - spi2_30) ** 5 + (10 - spi3_30) ** 5) ** Decimal(0.2) >= 0 else 0
    return spi_30


def calculate_spi_cri_with_score(c, r, i, level_name="보조간선"):
    c, r, i = Decimal(c), Decimal(r), Decimal(i)
    spi1_30 = 10 - (Decimal(1.667) * (c ** Decimal(0.38))) if (10 - (
            Decimal(1.667) * (c ** Decimal(0.38)))) > 0 else 0
    spi2_30 = 10 - (Decimal(0.267) * r) if (10 - (Decimal(0.267) * r)) else 0
    if level_name == "도시고속":
        spi3_30 = 10 - Decimal(0.8) * i if 10 - Decimal(0.8) * i >= 0 else 0
    elif level_name == "보조간선":
        spi3_30 = 10 - Decimal(0.667) * i if 10 - Decimal(0.667) * i >= 0 else 0
    else:
        spi3_30 = 10 - Decimal(0.727) * i if 10 - Decimal(0.727) * i >= 0 else 0
    spi_30 = 10 - ((10 - spi1_30) ** 5 + (10 - spi2_30) ** 5 + (10 - spi3_30) ** 5) ** Decimal(0.2) if 10 - (
            (10 - spi1_30) ** 5 + (10 - spi2_30) ** 5 + (10 - spi3_30) ** 5) ** Decimal(0.2) >= 0 else 0
    return crack_score, rutting_score, iri_score, LrPCI if LrPCI > 0 else 0


def calculate_LrPCI_cri_with_score(c, r, i, level_name="지방도"):
    print(level_name)
    if level_name == "국도":
        crack_a = 1.154
        crack_b = 0.46
        rutting_rd = 15.0
        iri_rd = 5.0
    elif level_name == "지방도" or level_name == "국지도":
        crack_a = 1.154
        crack_b = 0.46
        rutting_rd = 20.0
        iri_rd = 6.0
    elif level_name == "시도":
        crack_a = 1.154
        crack_b = 0.46
        rutting_rd = 15.0
        iri_rd = 6.0
    elif level_name == "군도":
        crack_a = 0.748
        crack_b = 0.56
        rutting_rd = 20.0
        iri_rd = 6.5
    elif level_name == "면리도":
        crack_a = 0.748
        crack_b = 0.56
        rutting_rd = 25.0
        iri_rd = 7.0
    crack_score = 10 - crack_a * pow(c, crack_b)
    rutting_score = 10 - (4 / rutting_rd) * r
    iri_score = 10 - (4 / iri_rd) * i
    LrPCI = 10 - pow((pow(10 - crack_score, 5) + pow(10 - rutting_score, 5) + pow(10 - iri_score, 5)), 0.2)
    return crack_score, rutting_score, iri_score, LrPCI if LrPCI > 0 else 0


def calculate_LrPCI_cri(c, r, i, level_name="지방도"):
    if level_name == "국도":
        crack_a = 1.154
        crack_b = 0.46
        rutting_rd = 15.0
        iri_rd = 5.0
    elif level_name == "지방도" or level_name == "국지도":
        crack_a = 1.154
        crack_b = 0.46
        rutting_rd = 20.0
        iri_rd = 6.0
    elif level_name == "시도":
        crack_a = 1.154
        crack_b = 0.46
        rutting_rd = 15.0
        iri_rd = 6.0
    elif level_name == "군도":
        crack_a = 0.748
        crack_b = 0.56
        rutting_rd = 20.0
        iri_rd = 6.5
    elif level_name == "면리도":
        crack_a = 0.748
        crack_b = 0.56
        rutting_rd = 25.0
        iri_rd = 7.0
    crack_score = 10 - crack_a * pow(c, crack_b)
    rutting_score = 10 - (4 / rutting_rd) * r
    iri_score = 10 - (4 / iri_rd) * i
    LrPCI = 10 - pow((pow(10 - crack_score, 5) + pow(10 - rutting_score, 5) + pow(10 - iri_score, 5)), 0.2)
    return LrPCI if LrPCI > 0 else 0


def how_to_fix_local(c, fc, r, i, area):
    if r > 20.0:
        if fc >= 15.0:
            how_to_fix = "절삭 5cm + 개질 5cm"
            price = 4.5 * area / 100
        else:
            how_to_fix = "일반 10cm"
            price = 3.5 * area / 100
    elif c > 40.0:
        if r >= 13.0:
            how_to_fix = "일반 10cm"
            price = 3.5 * area / 100
        else:
            how_to_fix = "개질 5cm"
            price = 3.0 * area / 100
    elif c > 10.0 or r > 13.0:
        how_to_fix = "일반 5cm"
        price = 2.0 * area / 100
    elif i > 6.0:
        how_to_fix = "표면 처리"
        price = 0.6 * area / 100
    else:
        how_to_fix = None
        price = 0
    return how_to_fix, round(price, 1)