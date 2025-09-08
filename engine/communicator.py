class Communicator:
    def __init__(self):
        self.agents = {}  # name -> agent object
        self.message_queue = {}  # name -> list of (sender, message)

    def register(self, name, agent):
        self.agents[name] = agent
        self.message_queue[name] = []
        print(f"[Communicator] ✅ Registered agent: {name}")

    def send_message(self, sender_name, receiver_name, message):
        if receiver_name in self.agents:
            print(f"[{sender_name} ➤ {receiver_name}] 📩 {message}")
            self.message_queue[receiver_name].append((sender_name, message))

            # If the receiver has a message handler
            receiver = self.agents[receiver_name]
            if hasattr(receiver, "receive_message"):
                receiver.receive_message(sender_name, message)
        else:
            print(f"[{sender_name}] ❌ ERROR: Receiver '{receiver_name}' not registered.")

    async def get_messages(self, receiver_name):
        if receiver_name not in self.message_queue:
            print(f"[Communicator] ⚠️ No message queue found for {receiver_name}.")
            return []
        messages = self.message_queue[receiver_name]
        self.message_queue[receiver_name] = []
        return messages

    def list_agents(self):
        return list(self.agents.keys())