@echo off
rem install redis on windows using choco
rem choco install redis-64

rem run redis
redis-server --daemonize yes

rem testing locally
rem redis-cli
rem SET foo bar
rem GET foo