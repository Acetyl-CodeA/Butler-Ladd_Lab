#define ALEXQCAMLIBRARY_EXPORTS

#include <cstdint>
#include <cstdio>
#include <iostream>
#include <fstream>
#include <QImgTypes.h>
#include <QCamAPI.h>
#include <QCamImgfnc.h>
#include <String>

#pragma comment(lib, "QCamDriver.lib")

#ifdef ALEXQCAMLIBRARY_EXPORTS
#define ALEXQCAMLIBRARY_API extern "C" __declspec(dllexport)
#else
#define ALEXQCAMLIBRARY_API extern "C" __declspec(dllimport)
#endif

using namespace std;

ALEXQCAMLIBRARY_API unsigned long PostProcessedFrameSize() {
	QCam_Err loadDriverError = QCam_LoadDriver();
	QCam_CamListItem list[10];
	unsigned long listLen = sizeof(list) / sizeof(list[0]);
	QCam_Err camListError = QCam_ListCameras(list, &listLen);
	QCam_Handle myHandle;
	QCam_Err openCamError = QCam_OpenCamera(list[0].cameraId, &myHandle);
	QCam_SettingsEx mySettings; // Create and allocate the settings structure
	QCam_CreateCameraSettingsStruct(&mySettings);
	QCam_InitializeCameraSettings(myHandle, &mySettings);
	QCam_SetParam((QCam_Settings*)&mySettings, qprmDoPostProcessing, 1);
	QCam_SetParam((QCam_Settings*)&mySettings, qprmPostProcessImageFormat, qfmtBgrx32);
	QCam_SendSettingsToCam(myHandle, (QCam_Settings*)&mySettings);
	QCam_Frame origFrame;
	unsigned long sizeInBytes;
	QCam_Err infoError = QCam_GetInfo(myHandle, qinfImageSize, &sizeInBytes);
	QCam_ReleaseCameraSettingsStruct(&mySettings);
	QCam_Err closeCamError = QCam_CloseCamera(myHandle);
	QCam_ReleaseDriver();
	return sizeInBytes;
}

ALEXQCAMLIBRARY_API void TakePicture(long errorArray[6], char* charout,double gain, double exposure) {
	QCam_Err loadDriverError = QCam_LoadDriver();
	errorArray[0] = loadDriverError;
	QCam_CamListItem list[10];
	unsigned long listLen = sizeof(list) / sizeof(list[0]);
	QCam_Err camListError = QCam_ListCameras(list, &listLen);
	errorArray[1] = camListError;
	if ((listLen > 0) && (list[0].isOpen == false))
	{
		QCam_Handle myHandle;
		
		QCam_Err openCamError = QCam_OpenCamera(list[0].cameraId, &myHandle);
		errorArray[2] = openCamError;

		QCam_SettingsEx mySettings; // Create and allocate the settings structure
		QCam_CreateCameraSettingsStruct(&mySettings);
		QCam_InitializeCameraSettings(myHandle, &mySettings);
		
		//turn on post processing first
		QCam_SetParam((QCam_Settings*)&mySettings, qprmDoPostProcessing, 1);
		//set up the post processing image format to qfmtBgrx32 which is the common windows format, perfect!
		QCam_SetParam((QCam_Settings*)&mySettings, qprmPostProcessImageFormat, qfmtBgrx32);
		//set up the bayer interpolation algorithm
		QCam_SetParam((QCam_Settings*)&mySettings, qprmPostProcessBayerAlgorithm, qcBayerInterpAvg4);
		//choose gain
		QCam_SetParam((QCam_Settings*)&mySettings, qprmNormalizedGain, gain);
		//choose exposure in microseconds
		QCam_SetParam((QCam_Settings*)&mySettings, qprmExposure, exposure);
		// Send settings to the camera
		QCam_SendSettingsToCam(myHandle, (QCam_Settings*)&mySettings);
		
		//unsigned long processedSize;
		//unsigned long ccdh;
		//QCam_GetInfo(myHandle, qinfPostProcessImageSize, &processedSize);
		//QCam_Frame processedFrame;
		//processedFrame.pBuffer = new byte[processedSize];
		//processedFrame.bufferSize = processedSize;

		QCam_Frame origFrame;
		unsigned long sizeInBytes;
		QCam_Err infoError = QCam_GetInfo(myHandle, qinfImageSize, &sizeInBytes);
		errorArray[3] = infoError;
		
		origFrame.pBuffer = new unsigned char[sizeInBytes];
		origFrame.bufferSize = sizeInBytes;
		
		QCam_Err grabFrameError = QCam_GrabFrame(myHandle, &origFrame);
		errorArray[4] = grabFrameError;

		//charout = (char*)origFrame.pBuffer;
		memcpy(charout, origFrame.pBuffer, origFrame.bufferSize * sizeof(char));

		//std::ofstream file("Lib-side testing file.txt", std::ios::binary);
		//file.write(charout, sizeInBytes);

		QCam_ReleaseCameraSettingsStruct(&mySettings);
		QCam_Err closeCamError = QCam_CloseCamera(myHandle);
		errorArray[5] = closeCamError;
		QCam_ReleaseDriver();
		return;
	}
	charout = (char*)"Failed To Open Camera";
	QCam_ReleaseDriver();
	return;
}

