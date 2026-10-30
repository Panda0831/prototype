import httpx

class PeerManager:
    def __init__(self, node_address: str):
        self.peers = set()  # Set of peer URLs (e.g., "http://localhost:8001")
        self.node_address = node_address

    def add_peer(self, peer_url: str):
        if peer_url != self.node_address:
            self.peers.add(peer_url)
            print(f" [+] Peer ajouté : {peer_url}")

    def get_peers(self):
        return list(self.peers)

    async def broadcast_transaction(self, transaction):
        """Diffuse une transaction à tous les pairs."""
        for peer in self.peers:
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(f"{peer}/api/p2p/transaction", json=transaction.to_dict())
            except Exception as e:
                print(f" [!] Erreur broadcast vers {peer}: {e}")

    async def broadcast_block(self, block):
        """Diffuse un bloc miné à tous les pairs."""
        for peer in self.peers:
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(f"{peer}/api/p2p/block", json=block.to_dict())
            except Exception as e:
                print(f" [!] Erreur broadcast bloc vers {peer}: {e}")
