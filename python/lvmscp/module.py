import sys
import uuid

from clu.actor import AMQPClient
from cluplus.proxy import Proxy


class API:
    def ping():

        try:
            amqpc = AMQPClient(name=f"{sys.argv[0]}.proxy-{uuid.uuid4().hex[:8]}")

            lvmscp = Proxy(amqpc, "lvmscp")
            lvmscp.start()

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        # sequential
        try:
            result = lvmscp.ping()

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        print(result)
        return result

    def status():

        try:
            amqpc = AMQPClient(name=f"{sys.argv[0]}.proxy-{uuid.uuid4().hex[:8]}")

            lvmscp = Proxy(amqpc, "lvmscp")
            lvmscp.start()

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        # sequential
        try:
            result = lvmscp.status()

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        print(result)
        return result

    def exposure(
        exptime=0.0, Nexp=1, imtype=None, shutter=True, metadata=None, ccdmodes=None
    ):

        try:
            amqpc = AMQPClient(name=f"{sys.argv[0]}.proxy-{uuid.uuid4().hex[:8]}")

            lvmscp = Proxy(amqpc, "lvmscp")
            lvmscp.start()

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        # sequential
        try:
            result = lvmscp.exposure(Nexp, imtype, exptime, "sp1")

        except Exception as e:
            amqpc.log.error(f"Exception: {e}")

        print(result)
        return result
