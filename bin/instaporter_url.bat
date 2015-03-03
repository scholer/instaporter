@echo off

call activate py3pip

REM pause

REM python %~dp0\..\gelutils\gelannotator_gui.py %1

REM instap just imports the instaporter.instaporter module and executes the main function:

REM You can add config params here:

REM python %~dp0\instap.py url %1
REM with argument:

python %~dp0\instap.py --loglevel INFO url %1


REM TEST INVOCATIONS:

REM Rothemund:
REM python %~dp0\instap.py --loglevel INFO url http://www.nature.com/nature/journal/v440/n7082/full/nature04586.html

REM DNA-Box:
REM python %~dp0\instap.py --loglevel INFO url http://www.nature.com/nature/journal/v459/n7243/full/nature07971.html

REM Circular RNA: http://www.nature.com/nature/journal/v495/n7441/full/nature11993.html
REM python %~dp0\instap.py --loglevel INFO url http://www.nature.com/nature/journal/v495/n7441/full/nature11993.html

IF ERRORLEVEL 1 pause

pause
