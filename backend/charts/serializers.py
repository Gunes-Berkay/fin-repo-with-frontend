# serializers.py
from rest_framework import serializers
from .models import StockData

from rest_framework import serializers

class DynamicTableSerializer(serializers.Serializer):
    datetime = serializers.CharField()
    symbol = serializers.CharField()
    open = serializers.FloatField()
    high = serializers.FloatField()
    low = serializers.FloatField()
    close = serializers.FloatField()
    volume = serializers.FloatField()
    rsi_14 = serializers.FloatField()
    macd = serializers.FloatField()
    macd_signal = serializers.FloatField()
    stoch_k = serializers.FloatField()
    stoch_d = serializers.FloatField()
    cmf = serializers.FloatField()
    cci = serializers.FloatField()
    mfi = serializers.FloatField()
    obv = serializers.FloatField()
    dmi_positive = serializers.FloatField()
    dmi_negative = serializers.FloatField()
    adx = serializers.FloatField()
    v_macd = serializers.FloatField()
    v_macd_signal = serializers.FloatField()
    Bearish_RSI_Divergence = serializers.BooleanField()
    Bear_Divergence_CMF = serializers.BooleanField()
    Bear_Divergence_MACD = serializers.BooleanField()
    Bear_Divergence_CCI = serializers.BooleanField()
    Bear_Divergence_MFI = serializers.BooleanField()
    Bear_Divergence_OBV = serializers.BooleanField()
    Bear_DIOSC_Divergence = serializers.BooleanField()
    Bear_VMACD_Divergence = serializers.BooleanField()
    Bull_Divergence = serializers.BooleanField()
    Bull_CMF_Divergence = serializers.BooleanField()
    Bull_MACD_Divergence = serializers.BooleanField()
    Bull_CCI_Divergence = serializers.BooleanField()
    Bull_MFI_Divergence = serializers.BooleanField()
    Bull_OBV_Divergence = serializers.BooleanField()
    Bull_DIOSC_Divergence = serializers.BooleanField()
    Bull_VMACD_Divergence = serializers.BooleanField()
    Hidden_Bear_RSI_Divergence = serializers.BooleanField()
    Hidden_Bear_MFI_Divergence = serializers.BooleanField()
    Hidden_Bear_MACD_Divergence = serializers.BooleanField()
    Hidden_Bear_CCI_Divergence = serializers.BooleanField()
    Hidden_Bear_OBV_Divergence = serializers.BooleanField()
    Hidden_Bear_VMACD_Divergence = serializers.BooleanField()
    Hidden_Bull_RSI_Divergence = serializers.BooleanField()
    Hidden_Bull_MFI_Divergence = serializers.BooleanField()
    Hidden_Bull_MACD_Divergence = serializers.BooleanField()
    Hidden_Bull_CCI_Divergence = serializers.BooleanField()
    Hidden_Bull_OBV_Divergence = serializers.BooleanField()
    Hidden_Bull_VMACD_Divergence = serializers.BooleanField()
    Bearish_Total = serializers.IntegerField()
    Bull_Total = serializers.IntegerField()
    Hidden_Bear_Total = serializers.IntegerField()
    Hidden_Bull_Total = serializers.IntegerField()

