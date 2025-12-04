from pydantic import BaseModel, Field, PositiveInt
import json
import os

BASE_FOLDER = 'Data'
GUILD_MEMBER_CONFIG_FOLDER = 'GuildMemberConfig'
os.makedirs(f"{BASE_FOLDER}/{GUILD_MEMBER_CONFIG_FOLDER}", exist_ok=True)

class GuildMemberConfig(BaseModel):
    guild_id: int = Field()
    id: int = Field()

    chat_experience: int = Field(default=0)

    buckshot_wins: int = Field(default=0)
    buckshot_losses: int = Field(default=0)
    buckshot_money: int = Field(default=0)
    

    def save(self) -> None:
        with open('/'.join(self.get_path(self.guild_id, self.id)), 'w') as fl:
            json.dump(self.model_dump(mode='json'), fl)

    @classmethod
    def get_path(cls, guild_id, _id) -> list[str]:
        return [BASE_FOLDER, GUILD_MEMBER_CONFIG_FOLDER, f'{guild_id}_{_id}.json']

    @classmethod
    def get(cls, guild_id, _id) -> GuildMemberConfig:
        with open('/'.join(cls.get_path(guild_id, _id)), 'r') as fl:
            file_contents = fl.read()
        
        return GuildMemberConfig.model_validate_json(file_contents)
    
    
        
