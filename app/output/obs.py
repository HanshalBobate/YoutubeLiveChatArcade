import asyncio

import obsws_python as obs


class OBSOutput:
    def __init__(self, host, port, password, source_name):
        self.source_name = source_name
        try:
            self.cl = obs.ReqClient(host=host, port=port, password=password)
            print("Connected to OBS")
        except Exception as e:
            print(f"Warning: Could not connect to OBS: {e}")
            self.cl = None

    async def update_text(self, text: str):
        if self.cl:
            try:
                # Run in executor because obsws_python is synchronous
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None, 
                    self.cl.set_input_settings, 
                    self.source_name, 
                    {"text": text}, 
                    True
                )
            except Exception as e:
                print(f"OBS Update Error: {e}")

    def update_text_sync(self, text: str):
        if self.cl:
            try:
                self.cl.set_input_settings(
                    self.source_name, 
                    {"text": text}, 
                    True
                )
            except Exception as e:
                print(f"OBS Update Error: {e}")
