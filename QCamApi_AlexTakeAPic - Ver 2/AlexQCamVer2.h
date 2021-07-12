
// AlexQCam.h - Contains declarations of the TakePicture function
#pragma once

#ifdef ALEXQCAMLIBRARY_EXPORTS
#define ALEXQCAMLIBRARY_API extern "C" __declspec(dllexport)
#else
#define ALEXQCAMLIBRARY_API extern "C" __declspec(dllimport)
#endif

ALEXQCAMLIBRARY_API void TakePicture(long errorArray[6],char* charout,double gain, double exposure);
ALEXQCAMLIBRARY_API unsigned long PostProcessedFrameSize();