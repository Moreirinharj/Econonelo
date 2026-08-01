from database.conexao import conectar


def modificar_xp_personagem(personagem_id: int, delta: int) -> dict:
    """Modifica o XP de um personagem."""
    conn = conectar()
    cur = conn.cursor()
    
    # Buscar XP atual
    cur.execute("SELECT xp, nivel FROM personagens WHERE id = ?", (personagem_id,))
    row = cur.fetchone()
    
    if not row:
        conn.close()
        return {"sucesso": False, "msg": "Personagem não encontrado."}
    
    xp_atual = row["xp"]
    nivel_atual = row["nivel"]
    novo_xp = xp_atual + delta
    
    # Verificar se subiu de nível (100 XP por nível)
    novo_nivel = nivel_atual
    while novo_xp >= 100:
        novo_xp -= 100
        novo_nivel += 1
    
    # Atualizar
    cur.execute("UPDATE personagens SET xp = ?, nivel = ? WHERE id = ?", 
                (novo_xp, novo_nivel, personagem_id))
    conn.commit()
    conn.close()
    
    return {
        "sucesso": True,
        "xp_anterior": xp_atual,
        "xp_novo": novo_xp,
        "nivel_anterior": nivel_atual,
        "nivel_novo": novo_nivel,
        "subiu_nivel": novo_nivel > nivel_atual,
    }
