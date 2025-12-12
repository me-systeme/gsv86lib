# -*- coding: utf-8 -*-
__author__ = 'Dennis Rump'
###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) 2015 Dennis Rump
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# Hiermit wird unentgeltlich, jeder Person, die eine Kopie der Software
# und der zugehörigen Dokumentationen (die "Software") erhält, die
# Erlaubnis erteilt, uneingeschränkt zu benutzen, inklusive und ohne
# Ausnahme, dem Recht, sie zu verwenden, kopieren, ändern, fusionieren,
# verlegen, verbreiten, unter-lizenzieren und/oder zu verkaufen, und
# Personen, die diese Software erhalten, diese Rechte zu geben, unter
# den folgenden Bedingungen:
#
# Der obige Urheberrechtsvermerk und dieser Erlaubnisvermerk sind in
# alle Kopien oder Teilkopien der Software beizulegen.
#
# DIE SOFTWARE WIRD OHNE JEDE AUSDRÜCKLICHE ODER IMPLIZIERTE GARANTIE
# BEREITGESTELLT, EINSCHLIESSLICH DER GARANTIE ZUR BENUTZUNG FÜR DEN
# VORGESEHENEN ODER EINEM BESTIMMTEN ZWECK SOWIE JEGLICHER
# RECHTSVERLETZUNG, JEDOCH NICHT DARAUF BESCHRÄNKT. IN KEINEM FALL SIND
# DIE AUTOREN ODER COPYRIGHTINHABER FÜR JEGLICHEN SCHADEN ODER SONSTIGE
# ANSPRUCH HAFTBAR ZU MACHEN, OB INFOLGE DER ERFÜLLUNG VON EINEM
# VERTRAG, EINEM DELIKT ODER ANDERS IM ZUSAMMENHANG MIT DER BENUTZUNG
# ODER SONSTIGE VERWENDUNG DER SOFTWARE ENTSTANDEN.
#
###############################################################################
# Interpret the GSV6 Seriell Kommunikation

from .GSV_Exceptions import *
from struct import *
from .GSV6_AnfrageCodes import anfrage_code_to_shortcut
import threading


class GSV6_seriall_lib:
    cachedConfig = {}
    cacheLock = None

    def __init__(self):
        self.cacheLock = threading.Lock()
        # now preinit cachedConfig
        self.cachedConfig['GetInterface'] = {}
        self.cachedConfig['AoutScale'] = {}
        self.cachedConfig['Zero'] = {}
        self.cachedConfig['UserScale'] = {}
        self.cachedConfig['UnitText'] = {}
        self.cachedConfig['UnitNo'] = {}
        self.cachedConfig['SerialNo'] = {}
        self.cachedConfig['DeviceHours'] = {}
        self.cachedConfig['DataRate'] = {}
        self.cachedConfig['FirmwareVersion'] = {}
        self.cachedConfig['UserOffset'] = {}
        self.cachedConfig['InputType'] = {}


    def encode_anfrage_frame(self, kommando, kommando_para=[]):
        # 0xAA=SyncByte; 0x50=Anfrage,Seriell,Length=0
        result = bytearray([0xAA, 0x90])
        result.append(kommando)
        if len(kommando_para) > 0:
            #result.extend(kommando_para.encode())
            result.extend(kommando_para)
            # update length
            result[1] = (result[1] | len(kommando_para))
        result.append(0x85)
        return result


    def convertToUint16_t(self, data):
        # H	= unsigned short; Python-Type: integer, size:2
        return unpack('>H', data)


    def convertToUint24_t(self, data):
        tmpData = bytearray([0x00])
        tmpData.extend(data)
        # I	= unsigned int; Python-Type: integer, size:4
        return unpack('>I', tmpData)

    def convertToUint32_t(self, data):
        length = len(data)
        if not ((length >= 4) and (length % 4) == 0):
            raise GSV6_ConversionError_Exception('uint32_t')
            return

        # I	= unsigned int; Python-Type: integer, size:4
        return unpack('>' + str(int(length / 4)) + "I", data)
        #return unpack('>' + "I", data)

    def convertToFloat(self, data):
        length = len(data)
        if not ((length >= 4) and (length % 4) == 0):
            raise GSV6_ConversionError_Exception('float')

        # > = Big-Endian; f	= float; Python-Type: float, size:4
        #return unpack('>' + bytearray(length / 4) + "f", data)
        #return unpack('>' + str(length / 4) + "f", data)
        return unpack('>' + str(int(length / 4)) + "f", data)

    def convertFloatToBytes(self, data):
        # > = Big-Endian; f	= float; Python-Type: float, size:4
        return bytearray(pack('>f', data))

    def convertUInt8ToBytes(self, data):
        # > = Big-Endian; B	= uint8; Python-Type: int, size:4 -> 1
        return pack('>B', data)

    def convertUInt16ToBytes(self, data):
        # > = Big-Endian; B	= uint8; Python-Type: int, size:4 -> 1
        return pack('>H', data)

    def convertUInt32ToBytes(self, data):
        # > = Big-Endian; B	= uint8; Python-Type: int, size:4 -> 1
        return pack('>I', data)

    def convertIntToBytes(self, data):
        # > = Big-Endian; f	= float; Python-Type: float, size:4
        return bytearray(pack('>I', data))

    def convertToString(self, data):
        length = len(data)
        if not length >= 1:
            raise GSV6_ConversionError_Exception('string')
            return

        # s	= char[]; Python-Type: strng, size:*
        return unpack('>' + str(length) + 's', data)

    def buildGetInterface(self, uebertragung=None):
        if uebertragung is None:
            return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('GetInterface'), [0x00])
        elif uebertragung:
            return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('GetInterface'), [0x02])
        else:
            return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('GetInterface'), [0x01])

    def buildReadAoutScale(self, channelNo):
        return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('ReadAoutScale'), [channelNo])

    def buildWriteAoutScale(self, channelNo, AoutScale):
        data = bytearray([channelNo])
        data.extend(AoutScale)
        return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('WriteAoutScale'), data)

    def buildReadZero(self, channelNo):
        return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('ReadZero'), [channelNo])

    def buildWriteZero(self, channelNo, zero):
        data = bytearray([channelNo])
        data.extend(zero)
        return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('WriteZero'), data)

    def buildReadUserScale(self, channelNo):
        return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('ReadUserScale'), [channelNo])

    def buildWriteUserScale(self, channelNo, userScale):
        data = bytearray([channelNo])
        data.extend(userScale)
        return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('WriteUserScale'), data)

    def buildStartTransmission(self):
        return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('StartTransmission'))

    def buildStopTransmission(self):
        return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('StopTransmission'))

    def buildGetUnitText(self, slot):
        return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('GetUnitText'), [
            slot])

    def buildSetUnitText(self, text, slot=0):
        if slot <= 0 or slot > 1:
            data = bytearray([0x00, 0x00])
        else:
            data = bytearray([0x01, 0x00])
        data.extend(bytearray(text.encode('ascii', 'replace')))
        return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('SetUnitText'), data)

    def buildGetUnitNo(self, channelNo):
        return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('GetUnitNo'), [channelNo])

    def buildWriteUnitNo(self, channelNo, unitNo):
        data = bytearray([channelNo])
        data.append(unitNo)
        return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('SetUnitNo'), data)

    def buildGetSerialNo(self):
        return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('GetSerialNo'))

    def buildGetDeviceHours(self, slot=0):
        return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('GetDeviceHours'), [slot])

    def buildGetDataRate(self):
        return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('ReadDataRate'))

    def buildWriteDataRate(self, dataRate):
        #dataRate = str(dataRate)
        return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('WriteDataRate'), dataRate)

    def buildWriteSaveAll(self, slot=0):
        return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('SaveAll'), [slot])

    def buildWriteSetZero(self, channelNo):
        return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('SetZero'), [channelNo])

    def buildgetFirmwareVersion(self):
        return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('GetFirmwareVersion'))

    def buildReadUserOffset(self, channelNo):
        return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('ReadUserOffset'), [channelNo])

    def buildWriteUserOffset(self, channelNo, userOffset):
        data = bytearray([channelNo])
        data.extend(userOffset)
        return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('WriteUserOffset'), data)

    def buildReadInputType(self, channelNo, sensindex=0x00):
        #data = bytearray([self.convertUInt8ToBytes(channelNo), self.convertUInt8ToBytes(sensindex)])
        data = bytearray([channelNo, sensindex])
        return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('GetInputType'), data)

    def buildWriteInputTypeGSV6(self, channelNo, sensIndex, inputType, isGSV_6=True):
        if isGSV_6:
            channelNo = 0
        data = bytearray([channelNo,])
        data.extend(inputType)
        return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('MEwriteInputRange'), data)

    #def buildSetInputTypeGSV8(self, channelNo, sensIndex, inputType):
    def buildSetInputTypeGSV8(self, channelNo, inputType):
        data = bytearray([channelNo, inputType])
        return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('SetInputType'), data)

    def buildSetMEid(self, minor):
        magicCode = bytearray([0x4D, 0x45, 0x69, minor])
        return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('MEsetID'), magicCode)

    def buildGetTXMode(self, index):
        return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('SetTXMode'), [index])

    def buildSetTXMode(self, index, mode):
        data = bytearray([index])
        data.extend(mode)
        return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('SetTXMode'), data)

    def buildSetTXModeToFloat(self):
        data = bytearray([0x00, 0x10])
        return self.buildSetTXMode(1, data)

    def buildSetTXModeToInt32(self):
        data = bytearray([0x00, 0x04])
        return self.buildSetTXMode(1, data)

    def buildSetTXModeToInt16(self):
        data = bytearray([0x00, 0x01])
        return self.buildSetTXMode(1, data)

    def buildGetValue(self):
        return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('GetValue'))

    def buildGetDIOdirection(self, gruppe):
        return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('GetDIOdirection'),[gruppe])

    def buildSetDIOdirection(self, gruppe, direction):
        # level umwandeln
        #data = bytearray([self.convertUInt8ToBytes(gruppe)])
        data = bytearray([gruppe])
        #data.append(self.convertUInt8ToBytes(direction))
        data.append(direction)
        return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('SetDIOdirection'), data)

    def buildGetDIOlevel(self, IOPin):
        #data = bytearray([self.convertUInt8ToBytes(IOPin)])
        data = bytearray([IOPin])
        return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('GetDIOlevel'),data)

    def buildSetDIOlevel(self, IOPin, newlevel):
        #data = bytearray([self.convertUInt8ToBytes(IOPin)])
        data = bytearray([IOPin])
        data.extend(self.convertUInt16ToBytes(newlevel))
        return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('SetDIOlevel'), data)

    def buildGetDIOinitialLevel(self, IOPin):
        #data = bytearray([self.convertUInt8ToBytes(IOPin)])
        data = bytearray([IOPin])
        return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('GetDIOinitialLevel'),data)

    def buildSetDIOinitialLevel(self, IOPin, newlevel):
        #data = bytearray([self.convertUInt8ToBytes(IOPin)])
        data = bytearray([IOPin])
        data.extend(self.convertUInt16ToBytes(newlevel))
        return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('SetDIOinitialLevel'), data)

    def buildGetMode(self):
        return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('GetMode'))

    def buildSetMode(self, ModeFlags_32Bit):
        return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('SetMode'), ModeFlags_32Bit)

    def buildReadDIOthreshold(self, IOPin,upper_or_lower_trigger):
        #data = bytearray([self.convertUInt8ToBytes(IOPin), self.convertUInt8ToBytes(upper_or_lower_trigger)])
        data = bytearray([IOPin, upper_or_lower_trigger])
        return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('ReadDIOthreshold'),data)

    def buildWriteDIOthreshold(self, IOPin, upper_or_lower_trigger, threshold_value):
        #data = bytearray([self.convertUInt8ToBytes(IOPin), self.convertUInt8ToBytes(upper_or_lower_trigger)])
        data = bytearray([IOPin, upper_or_lower_trigger])
        data.extend(self.convertFloatToBytes(threshold_value))
        return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('WriteDIOthreshold'), data)

    def buildGetDIOtype(self, IOPin):
        #data = bytearray([self.convertUInt8ToBytes(IOPin)])
        data = bytearray([IOPin])
        return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('GetDIOtype'),data)

    def buildSetDIOtype(self, IOPin, DIOtype, assignedDMSchannel):
        #data = bytearray([self.convertUInt8ToBytes(IOPin)])
        data = bytearray([IOPin])
        if(type(DIOtype) is bytearray):
            data.extend(DIOtype)
        else:
            data.extend(self.convertUInt32ToBytes(DIOtype)[1:])
        #data.append(self.convertUInt8ToBytes(assignedDMSchannel))
        data.append(assignedDMSchannel)
        return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('SetDIOtype'), data)

    def buildGet1WireTempValue(self):
        return self.encode_anfrage_frame(anfrage_code_to_shortcut.get('Get1WireTempValue'), [])
