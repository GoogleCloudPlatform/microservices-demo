#!/bin/sh
### ====================================================================== ###
##                                                                          ##
##  SoapUI TestCaseRunner Bootstrap Script                                  ##
##                                                                          ##
### ====================================================================== ###

### $Id$ ###

DIRNAME=`dirname $0`

# OS specific support (must be 'true' or 'false').
cygwin=false;
case "`uname`" in
    CYGWIN*)
        cygwin=true
        ;;
esac

# Setup SOAPUI_HOME
if [ "x$SOAPUI_HOME" = "x" ]
then
    # get the full path (without any relative bits)
    SOAPUI_HOME=`cd $DIRNAME/..; pwd`
fi
export SOAPUI_HOME

SOAPUI_CLASSPATH=./integration-tests/soapUI/soapui-5.7.1.jar
JFXRTPATH=`java -cp $SOAPUI_CLASSPATH com.eviware.soapui.tools.JfxrtLocator`
SOAPUI_CLASSPATH=$JFXRTPATH:$SOAPUI_CLASSPATH


JAVA_OPTS="-Xms128m -Xmx1024m -Dsoapui.properties=soapui.properties -Dsoapui.home=$SOAPUI_HOME/bin"

#CVE-2021-44228
JAVA_OPTS="$JAVA_OPTS -Dlog4j2.formatMsgNoLookups=true"

#JAVA 16
JAVA_OPTS="$JAVA_OPTS --illegal-access=permit"

if [ $SOAPUI_HOME != "" ]
then
    JAVA_OPTS="$JAVA_OPTS -Dsoapui.ext.libraries=$SOAPUI_HOME/bin/ext"
    JAVA_OPTS="$JAVA_OPTS -Dsoapui.ext.listeners=$SOAPUI_HOME/bin/listeners"
    JAVA_OPTS="$JAVA_OPTS -Dsoapui.ext.actions=$SOAPUI_HOME/bin/actions"
fi

export JAVA_OPTS
# For Cygwin, switch paths to Windows format before running java
if [ $cygwin = "true" ]
then
    SOAPUI_HOME=`cygpath --path --dos "$SOAPUI_HOME"`
    SOAPUI_CLASSPATH=`cygpath --path --dos "$SOAPUI_CLASSPATH"`
fi

echo ================================
echo =
echo = SOAPUI_HOME = $SOAPUI_HOME
echo =
echo ================================
#export LAB_ID="${params.sl_labid}"
#export TOKEN="${params.sl_token}"
#sed -i 's/machine_dns/machine_dns1/' testrunner.sh

pwd

java -javaagent:sl-test-listener.jar -Dsl.token="${TOKEN}" -Dsl.labId="${LAB_ID}" -Dsl.testStage="Soapui Tests" $JAVA_OPTS -cp $SOAPUI_CLASSPATH com.eviware.soapui.tools.SoapUITestCaseRunner "$@"

