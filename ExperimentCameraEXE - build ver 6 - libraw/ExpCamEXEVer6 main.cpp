#include <list>
#include <cstdint>
#include <cstdio>
#include <stdlib.h>
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <sstream>
#include <winsock2.h>
#include <Windows.h>

//#include "libraw/libraw.h"

#include <libraw.h>

#include <QImgTypes.h>
#include <QCamAPI.h>
#include <QCamImgfnc.h>

using namespace std;

static void show_usage() { //not done yet
	std::cerr << "Usage: " << endl
		<< "Take a file containing an image and convert it to a TIF file." << endl
		<< "Parameters:" << endl
		<< "<int noFrames>" << endl
		<< "<float delay>" << endl
		<< "<float interval>" << endl
		<< "<float exposure>" << endl
		<< "<float gain>" << endl
		<< "<string destDirectory" << endl
		<< "<string startTime>" << endl
		<< "<int bayerEndiannessFlag>" << endl
		<< "<int blackLevel>" << endl
		<< "<string RGBPatternChoice>" << endl
		<< endl
		<< "noFrames = number of pictures to take in this burst" << endl
		<< "delay = delay before taking the first picture in the burst" << endl
		<< "interval = delay between each frame you take" << endl
		<< "exposure = time of exposure in microseconds" << endl
		<< "gain = camera gain (max 39)" << endl
		<< "destDirectory = path of TIF to be outputted (without extension)" << endl
		<< "startTime = start time of the burst, just for picture naming purposes" << endl
		<< "bayerEndiannessFlag = 0 or 1. 0 is little endian, 1 is big endian. The camera is likely little endian" << endl
		<< "blackLevel = a number to indicate black level, it should be 4*256, as there are 4 channels of 256" << endl
		<< "RGBPatternChoice = what encoding to interpret it with, options are:" << endl
		<< "RGGB, BGGR, GRBG, GBRG" << endl;
	return;
}

	int main(int argc, char** argv) { 
	//requires 10 arguments
	//return protocol is 0 is good, nonzero is bad
	
	if (argc != 11) 
	{
		show_usage();
		return 1; //1 is incorrect # of passed arguments failure
	}

	//using namespace System.Collections.Generic;
	int noFrames;
	bool arg1Suc = sscanf_s(argv[1], "%i", &noFrames);

	float delay; //in milliseconds
	bool arg2Suc = sscanf_s(argv[2], "%f", &delay);

	float interval; //in milliseconds
	bool arg3Suc = sscanf_s(argv[3], "%f", &interval);

	float exposure;
	bool arg4Suc = sscanf_s(argv[4], "%f", &exposure);

	float gain;
	bool arg5Suc = sscanf_s(argv[5], "%f", &gain);

	string destDirectory = argv[6];

	string startTime = argv[7];

	int bayerEndiannessFlag;
	bool arg8Suc = sscanf_s(argv[8], "%i", &bayerEndiannessFlag);
	
	int blackLevel;
	bool arg9Suc = sscanf_s(argv[9], "%i", &blackLevel);

	string RGBPatternChoice = argv[10];
	string pc = RGBPatternChoice;

	LibRaw_openbayer_patterns pattern;

	if (pc == "RGGB") {
		pattern = LIBRAW_OPENBAYER_RGGB;
	}
	else if (pc == "BGGR") {
		pattern = LIBRAW_OPENBAYER_BGGR;
	}
	else if (pc == "GRBG") {
		pattern = LIBRAW_OPENBAYER_GRBG;
	}
	else if (pc == "GBRG") {
		pattern == LIBRAW_OPENBAYER_GBRG;
	}
	else {
		cout << "Not valid RGB type" << endl;
		system("pause");

		return 2; //2 is error selecting rbg type
	}

	if (!( 
		arg1Suc
		&& arg2Suc
		&& arg3Suc
		&& arg4Suc
		&& arg5Suc
		&& arg8Suc
		&& arg9Suc
		)
		)
	{
		cout << "Failure to process an argument" << endl;
		cout << "Success at passing frame number: " <<arg1Suc << endl;
		cout << "Success at passing delay: " << arg2Suc << endl;
		cout << "Success at passing interval between frames: " << arg3Suc << endl;
		cout << "Success at passing exposure: " << arg4Suc << endl;
		cout << "Success at passing gain: " << arg5Suc << endl;
		cout << "Success at passing bayer endianness flag: " << arg8Suc << endl;
		cout << "Success at passing black level: " << arg9Suc << endl;

		system("pause");
		return 3; //3 is argument passing failure
	}

	int QerrArray[7] = { -1, -1, -1, -1, -1, -1, -1};

	QerrArray[0] = QCam_LoadDriver();

	QCam_CamListItem list[10];
	unsigned long listLen = sizeof(list) / sizeof(list[0]);

	QerrArray[1] = QCam_ListCameras(list, &listLen);

	//for the rest of this, != 0 is bad for returns
	if (QerrArray[0] || QerrArray[1]) {
		cout << "(0 is good here)" << endl;
		cout << "Load driver error code: " << QerrArray[0] << endl;
		cout << "Create camera list error code: " << QerrArray[1] << endl;
		QCam_ReleaseDriver();
		system("pause");
		return 4; //4 means failed to load driver or camera 
	}

	if (!((listLen > 0) && (list[0].isOpen == false))) {
		QerrArray[2] = 1;
		cout << "Could not find camera" << endl;
		QCam_ReleaseDriver();
		system("pause");
		return 5; //5 means failure to find the camera
	}

	QCam_Handle myHandle;
	QerrArray[3] = QCam_OpenCamera(list[0].cameraId, &myHandle);

	if (QerrArray[3]) {
		cout << "Could not open camera, error code: " << QerrArray[3] << endl;
		QCam_ReleaseDriver();
		system("pause");
		return 6; //6 means failure to open camera
	}

	//settings stuff
	QCam_SettingsEx mySettings; // Create and allocate the settings structure
	QCam_CreateCameraSettingsStruct(&mySettings);
	QCam_InitializeCameraSettings(myHandle, &mySettings);

	//turn on post processing first
	QCam_SetParam((QCam_Settings*)&mySettings, qprmDoPostProcessing, 1);

	//set up the post processing image format to qfmtBgrx32 which is the common windows format, perfect!
	QCam_SetParam((QCam_Settings*)&mySettings, qprmPostProcessImageFormat, qfmtBgrx32);
	//QCam_SetParam((QCam_Settings*)&mySettings, qprmPostProcessImageFormat, qfmtRgb24);

	//set up the bayer interpolation algorithm
	QCam_SetParam((QCam_Settings*)&mySettings, qprmPostProcessBayerAlgorithm, qcBayerInterpAvg4);

	//choose gain
	QCam_SetParam((QCam_Settings*)&mySettings, qprmNormalizedGain, gain);

	//choose exposure in microseconds
	QCam_SetParam((QCam_Settings*)&mySettings, qprmExposure, exposure);

	// Send settings to the camera
	QCam_SendSettingsToCam(myHandle, (QCam_Settings*)&mySettings);

	QCam_Frame origFrame;
	unsigned long sizeInBytes;
	QerrArray[4] = QCam_GetInfo(myHandle, qinfImageSize, &sizeInBytes);

	if (QerrArray[4]) {
		cout << "Could not get camera info, error code: " << QerrArray[4] << endl;
		QCam_ReleaseDriver();
		QCam_CloseCamera(myHandle);
		system("pause");
		return 7; //7 means error getting info
	}

	origFrame.pBuffer = new unsigned char[sizeInBytes];
	origFrame.bufferSize = sizeInBytes;

	Sleep(delay);

	LibRaw iProcessor;
	cout << "Libraw processor created" << endl;
	int librawRet;
	iProcessor.imgdata.params.output_tiff = 1;

	for (int i = 0; i < noFrames; i++) {

		QerrArray[5] = QCam_GrabFrame(myHandle, &origFrame);

		if (QerrArray[5] != 0)
		{
			cout << "Can't take picture" << endl;
			QCam_CloseCamera(myHandle);
			QCam_ReleaseDriver();
			system("pause");
			return 8; //8 is taking picture error
		}

		string destPath = destDirectory
			+ "/"
			+ startTime
			+ "_picNumber_"
			+ to_string(i + 1)
			+ ".tiff";

		librawRet = iProcessor.open_bayer(
			(uchar*)origFrame.pBuffer,
			origFrame.bufferSize,
			origFrame.width,
			origFrame.height,
			0, 0, 0, 0,
			bayerEndiannessFlag,
			pattern,
			0, //count of upper 0 bits
			0, //filter and orientation
			blackLevel
		);

		if (librawRet != LIBRAW_SUCCESS) {
			cout << "Failed to make the bayer buffer, error code: " << librawRet << endl;
			QCam_CloseCamera(myHandle);
			QCam_ReleaseDriver();
			system("pause");
			return 9; //failed to make the bayer buffer
		}

		if ((librawRet = iProcessor.unpack()) != LIBRAW_SUCCESS) {
			cout << "Bayer buffer unpacking error, code: " << librawRet << endl;
			QCam_CloseCamera(myHandle);
			QCam_ReleaseDriver();
			system("pause");
			return 10; //failed to unpack bayer buffer
		}

		if ((librawRet = iProcessor.dcraw_process()) != LIBRAW_SUCCESS) {
			cout << "Libraw processing error, code: " << librawRet << endl;
			QCam_CloseCamera(myHandle);
			QCam_ReleaseDriver();
			system("pause");
			return 11; //failed to process the image
		}

		if (LIBRAW_SUCCESS != (librawRet = iProcessor.dcraw_ppm_tiff_writer(destPath.c_str()))) {
			cout << "Tiff saving error: " << libraw_strerror(librawRet) << endl;
			QCam_CloseCamera(myHandle);
			QCam_ReleaseDriver();
			system("pause");
			return 12; //failed to save the image
		}
		else {
			cout << "Created the following tiff file: " << destPath << endl;
		}

		iProcessor.recycle();
		Sleep(interval);

	} 
	//end of for loop

	QCam_ReleaseCameraSettingsStruct(&mySettings);

	QCam_Err closeCamError = QCam_CloseCamera(myHandle);
	QerrArray[6] = closeCamError;

	QCam_ReleaseDriver();

	std::cout << "Success";

	return 0; //successfully done
}