import discord
from models.npc_modals.npc_basic_modal import NPCModalBase

class NPCCyberpunkSociaisModal(NPCModalBase):
  def __init__(self, npc_context):
    super().__init__(npc_context, title=f"🌐 Atributos Sociais de {npc_context.npc_name}")
    atributos = self.npc_data.get("atributos", {})

    self.atratividade = self.create_input("Atratividade (ATR)", "2-8", atributos.get("Atratividade"))
    self.sorte = self.create_input("Sorte (SOR)", "2-8", atributos.get("Sorte"))

    self.add_item(self.atratividade)
    self.add_item(self.sorte)

  def create_input(self, label, placeholder, default_value):
    return discord.ui.TextInput(
      label=label,
      placeholder=placeholder,
      default=str(default_value or ""),
      required=False,
    )

  async def on_submit(self, interaction: discord.Interaction):
    try:
      valores = {
        "Atratividade": self.atratividade.value,
        "Sorte": self.sorte.value
      }

      valores_int = {}
      for nome, valor in valores.items():
        if valor:
          v_int = int(valor)
          if not 2 <= v_int <= 800:
            raise ValueError(f"O valor de {nome} deve estar entre 2 e 8")
          valores_int[nome] = v_int

      self.npc_data.setdefault("atributos", {})
      self.npc_data["atributos"].update(valores_int)

      self.save()

      embed = discord.Embed(
        title=f"🌐 Atributos Sociais de {self.npc_context.npc_name}",
        description="**Cyberpunk**",
        color=0x9370DB
      )
      for nome, valor in valores_int.items():
        embed.add_field(name=f"✨ {nome}", value=f"`{valor}`", inline=True)

      embed.set_footer(text=f"NPC atualizado por {interaction.user.display_name}")

      await interaction.response.send_message(embed=embed, ephemeral=True)

    except ValueError as e:
      await interaction.response.send_message(f"❌ Erro: {e}. Certifique-se de usar apenas números entre 2 e 8.",
                                              ephemeral=True)