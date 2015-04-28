<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:gexf="http://www.gexf.net/1.1draft">
    <xsl:output method="xml"/>

  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="gexf:edge">
    <!-- determine numeric code for edge label attribute -->
    <xsl:variable name="edge_label_id"><xsl:value-of select="ancestor::gexf:graph/gexf:attributes[@class='edge']/gexf:attribute[@title='label']/@id"/></xsl:variable>
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <!-- if an edge label is present, add it as an attribute of the edge declaration -->
      <xsl:for-each select="gexf:attvalues/gexf:attvalue">
        <xsl:if test="@for = $edge_label_id">
           <xsl:attribute name="label"><xsl:value-of select="@value"/></xsl:attribute>
        </xsl:if>
      </xsl:for-each>
      <xsl:apply-templates select="node()"/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>