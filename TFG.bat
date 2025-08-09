set OSGEO4W_ROOT=C:/OSGeo4W
echo OSGEO4W_ROOT=%OSGEO4W_ROOT%

rem AÑADE AQUÍ LO QUE QUIERAS AL PATH
set path=%PATH%;%OSGEO4W_ROOT%\bin
set path=%PATH%;%OSGEO4W_ROOT%\apps\qgis-ltr\bin
set path=%PATH%;%WINDIR%\system32
set path=%PATH%;%WINDIR%\system32\WBem
set path=%PATH%;%WINDIR%\system32\WindowsPowerShell\v1.0
set path=%PATH%;%WINDIR%
set path=%PATH%;C:\Users\raulc\apps\nvim-nightly\bin
set path=%PATH%;C:\Program Files\Git\cmd
set path=%PATH%;%OSGEO4W_ROOT%\apps\qgis\bin
set path=%PATH%;C:\Users\raulc\AppData\Local\Programs\Microsoft VS Code\bin
set path=C:\OSGeo4W\apps\Python312;%PATH%
set path=%PATH%;C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\Tools
set path=%PATH%;C:\Users\raulc\scoop\persist\nodejs\bin
echo %PATH

rem EJECUTA TODOS LOS .BAT DE OSGEO4W/ETC/INI/
for %%f in ("%OSGEO4W_ROOT%\etc\ini\*.bat") do call "%%f"%

set QGIS_PREFIX_PATH=%OSGEO4W_ROOT:\=/%/apps/qgis-ltr
set GDAL_FILENAME_IS_UTF8=YES
rem Set VSI cache to be used as buffer, see #6448
set VSI_CACHE=TRUE
set VSI_CACHE_SIZE=1000000
set QT_PLUGIN_PATH=%OSGEO4W_ROOT%\apps\qgis-ltr\qtplugins;%OSGEO4W_ROOT%\apps\qt5\plugins
set PYTHONPATH=%OSGEO4W_ROOT%\apps\qgis-ltr\python;%PYTHONPATH%



rem List available o4w programs
rem but only if osgeo4w called without parameters
@echo on
rem @if [%1]==[] (echo run o-help for a list of available commands & cmd.exe /k) else (cmd.exe /k "%*")
start powershell -NoExit -Command "Set-Location 'C:\Users\raulc\Desktop\TFG25'"
exit /b
