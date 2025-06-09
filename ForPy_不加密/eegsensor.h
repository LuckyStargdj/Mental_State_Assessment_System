#ifndef EEGSENSOR_H
#define EEGSENSOR_H
#include "eegsensor_global.h"


#define ALPHA 0.98

struct dcFilter_t
{
  double w;
  double result;
};

struct LowPassbutterworthFilter_t
{
  double v[3];
  double result;
};

struct BandStopbutterworthFilter_t
{
  double v[5];
  double result;
};

struct BandStop100butterworthFilter_t
{
  double v[5];
  double result;
};

class EEGSENSORSHARED_EXPORT EEGSENSOR
{

    public:

        EEGSENSOR();

        double* ThreeLead_EEGSensor_DataFrameParse(unsigned char rawbyte[37], double SeriesPortLeadsDatas[3]);
        double* ThreeLead_EEGSensor_DataDSP(double RawEEGDataFp1FpzFp2[250*3], double DSPEEGDataFp1FpzFp2[250*3+54]);
        int* EEGQuality(double EEGDataFp1FpzFp2[250*3], int EEGQualityFlag[3]);

        dcFilter_t dcRemoval(double x, double prev_w, double alpha);
        void LowPassButterworthFilter(double x, LowPassbutterworthFilter_t * filterResult );
        void BandStopButterworthFilter( double x, BandStopbutterworthFilter_t * filterResult );
        void BandStop100ButterworthFilter( double x, BandStop100butterworthFilter_t * filterResult );

    private:

        dcFilter_t dcFilterIR6;                                        //去基线漂移
        LowPassbutterworthFilter_t LPFilterIR6;
        BandStopbutterworthFilter_t BSFilterIR6;                       //巴特沃斯带阻滤波 去50Hz工频
        BandStop100butterworthFilter_t BS100FilterIR6;                 //巴特沃斯带阻滤波 去100Hz工频


        dcFilter_t dcFilterIR7;                                        //去基线漂移
        LowPassbutterworthFilter_t LPFilterIR7;
        BandStopbutterworthFilter_t BSFilterIR7;                       //巴特沃斯带阻滤波 去50Hz工频
        BandStop100butterworthFilter_t BS100FilterIR7;                 //巴特沃斯带阻滤波 去100Hz工频


        dcFilter_t dcFilterIR8;                                        //去基线漂移
        LowPassbutterworthFilter_t LPFilterIR8;
        BandStopbutterworthFilter_t BSFilterIR8;                       //巴特沃斯带阻滤波 去50Hz工频
        BandStop100butterworthFilter_t BS100FilterIR8;                 //巴特沃斯带阻滤波 去100Hz工频


};


// 用于extern "C"的函数声明
#ifdef __cplusplus
extern "C" {
#endif

EEGSENSORSHARED_EXPORT double* ThreeLead_EEGSensor_DataFrameParse(unsigned char rawbyte[37], double SeriesPortLeadsDatas[3]);
EEGSENSORSHARED_EXPORT double* ThreeLead_EEGSensor_DataDSP(double RawEEGDataFp1FpzFp2[250*3], double DSPEEGDataFp1FpzFp2[250*3+54]);
EEGSENSORSHARED_EXPORT int* EEGQuality(double EEGDataFp1FpzFp2[250*3], int EEGQualityFlag[3]);

#ifdef __cplusplus
}
#endif
//=================================
#endif // EEGSENSOR_H
