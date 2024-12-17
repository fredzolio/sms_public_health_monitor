SELECT 
    epi.id_episodio,
    epi.subtipo,
    epi.entrada_data,
    epi.motivo_atendimento,
    epi.desfecho_atendimento,
    cond.id AS condicao_id,
    cond.resumo AS condicao_resumo,
    med.nome AS medicamento_administrado,
    loc.id_cnes AS estabelecimento_id,
    loc.endereco_latitude AS latitude,
    loc.endereco_longitude AS longitude
FROM 
    `rj-sms.saude_historico_clinico.episodio_assistencial` AS epi
LEFT JOIN 
    UNNEST(epi.condicoes) AS cond
LEFT JOIN 
    UNNEST(epi.medicamentos_administrados) AS med
JOIN 
    `rj-sms.saude_dados_mestres.estabelecimento` AS loc
ON 
    epi.estabelecimento.id_cnes = loc.id_cnes
WHERE 
    entrada_data = '{new_date}'
    AND epi.motivo_atendimento IS NOT NULL
    AND epi.desfecho_atendimento IS NOT NULL
    AND cond.id IS NOT NULL

--------------------------------------------------------------------------

SELECT 
    epi.id_episodio,
    epi.subtipo,
    epi.entrada_data,
    epi.motivo_atendimento,
    epi.desfecho_atendimento,
    cond.id AS condicao_id,
    cond.resumo AS condicao_resumo,
    med.nome AS medicamento_administrado,
    loc.id_cnes AS estabelecimento_id,
    loc.endereco_latitude AS latitude,
    loc.endereco_longitude AS longitude
FROM 
    `rj-sms.saude_historico_clinico.episodio_assistencial` AS epi
LEFT JOIN 
    UNNEST(epi.condicoes) AS cond
LEFT JOIN 
    UNNEST(epi.medicamentos_administrados) AS med
JOIN 
    `rj-sms.saude_dados_mestres.estabelecimento` AS loc
ON 
    epi.estabelecimento.id_cnes = loc.id_cnes
WHERE 
    entrada_data BETWEEN '{start_date}' AND '{end_date}'
    AND epi.motivo_atendimento IS NOT NULL
    AND epi.desfecho_atendimento IS NOT NULL
    AND cond.id IS NOT NULL